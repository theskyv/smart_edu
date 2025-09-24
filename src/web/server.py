import dotenv
from langchain_community.vectorstores.neo4j_vector import SearchType
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_deepseek import ChatDeepSeek
from langchain_huggingface import HuggingFaceEmbeddings

from configuration import config

dotenv.load_dotenv()

from langchain_core.prompts import PromptTemplate
from langchain_neo4j import Neo4jGraph, Neo4jVector


#https://python.langchain.com/docs/tutorials/graph/
class ChatService:
    def __init__(self):

        self.graph = Neo4jGraph(url=config.NEO4J_CONFIG['uri'],
                                username=config.NEO4J_CONFIG['auth'][0],
                                password=config.NEO4J_CONFIG['auth'][1])
        self.llm = ChatDeepSeek(model='deepseek-chat',api_key=config.DEEPSEEK_API_KEY)
        self.embedding_model = HuggingFaceEmbeddings(model_name='BAAI/bge-small-zh-v1.5',
                                                     encode_kwargs={'normalize_embeddings': True})
        self.json_parser = JsonOutputParser()
        self.str_parser = StrOutputParser()

        self.neo4j_vectors = self._init_neo4j_vectors() #🔥使用langchain提供查询工具

    def _init_neo4j_vectors(self):
        labels = ['CourseCategory','Subject','Course','Chapter','Paper','TestQuestion','Student','Video']
        return {label: self._create_neo4j_vector(label) for label in labels}


    #❗注意前提是index_name前缀和label保持一致(创建索引)
    def _create_neo4j_vector(self, label):
        index_name = f'{label.lower()}_vector_index'  # default index name
        keyword_index_name = f'{label.lower()}_full_text_index'  # default keyword index name

        return Neo4jVector.from_existing_index(
                self.embedding_model,
                url=config.NEO4J_CONFIG['uri'],
                username=config.NEO4J_CONFIG['auth'][0],
                password=config.NEO4J_CONFIG['auth'][1],
                index_name=index_name,
                keyword_index_name=keyword_index_name,
                search_type=SearchType.HYBRID,
            )


    def chat(self,question):
        #1.根据用户的question和图数据库的schema生成Cypher语句以及需要对齐的实体
        result = self._generate_cypher(question)
        cypher = result['cypher_query']
        print(cypher)
        entities_to_align = result['entities_to_align']

        #2.通过混合检索去做实体对齐
        aligned_entities= self._entity_align(entities_to_align)

        # 3.执行cypher语句
        query_result = self._execute_query(cypher, aligned_entities)

        # #4.根据用户问题和查询结果生成自然语言回复
        answer = self._generate_answer(question, query_result)
        return answer

    def _generate_cypher(self, question): #🔥json格式的提示词必须要用双引号
        prompt = '''
                 你是一个专业的Neo4j Cypher查询生成器,你的任务是根据用户问题生成一条Cypher查询语句,用于从知识图谱中获取回答用户问题所需的信息.
                 
                 用户问题:{question}
                 知识图谱结构信息:{schema_info}
                 
                 要求:
                 1.生成参数化Cypher查询语句,用param_0,param_1等代替具体值
                 2.识别需要对齐的实体
                 3.必须严格使用以下JSON格式输出结果
                 {{
                    "cypher_query": "生成的Cypher语句",
                    "entities_to_align":[
                      {{ 
                        "param_name": "param_0",
                        "entity": "原始实体名称",
                        "label": "节点类型"
                      }}
                    ]
                 }}
        '''
        prompt = PromptTemplate.from_template(prompt)
        prompt = prompt.format(question=question,schema_info=self.graph.schema)

        output = self.llm.invoke(prompt)

        result = self.json_parser.invoke(output)
        return result

    #{'cypher_query': 'MATCH (c:Course {name: $param_0})-[:BELONG]->(s:SubjectId)-[:BELONG]->(cc:CourseCategory)
    # RETURN cc.name AS category',

    # 'entities_to_align': [{'param_name': 'param_0', 'entity': 'python课程', 'label': 'Course'}]}
    def _entity_align(self, entities_to_align):
        '''
        实体对齐
        '''
        for index,entity_to_align in enumerate(entities_to_align):
            label = entity_to_align['label']
            entity = entity_to_align['entity']
            # import pdb;pdb.set_trace()
            aligned_entity = self.neo4j_vectors[label].similarity_search(entity,k=1)[0].page_content
            entities_to_align[index]['entity'] = aligned_entity  #🔥原地修改
        return entities_to_align
    
    def _execute_query(self, cypher, aligned_entities):
        params = {aligned_entity['param_name']: aligned_entity['entity'] for aligned_entity in aligned_entities} #❗字典
        return self.graph.query(cypher,params=params)

    def _generate_answer(self, question, query_result):
        #❗❗❗❗定义 prompt 时同时使用了 f-string 标记（f'''）和 format() 方法，这两种语法冲突了。
        prompt = '''
            你是一个教育培训领域的智能客服,精通IT和AI相关知识.根据用户问题,以及数据库查询结果生成回答。
            要求:
            1.回答简洁、准确,使用纯自然语言。
            2.不使用任何格式(如加粗**、斜体*、列表等),仅输出普通文本
            3.直接给出结论,无需额外冗余内容。
            用户问题:{question}
            数据库返回结果:{query_result}
        '''
        prompt = prompt.format(question=question,query_result=query_result)
        output = self.llm.invoke(prompt)
        return self.str_parser.invoke(output)



#👉当不需要参数化查询时，
#这段代码的工作逻辑可以概括为：LLM 生成无参数 Cypher + 空实体列表 → 实体对齐无操作 → 无参数执行 Cypher → 生成自然语言答案
if __name__ == '__main__':
    chat_service = ChatService()

    user_question = 'python课程属于什么类呢?'
    res = chat_service.chat(user_question)
    print(res)














