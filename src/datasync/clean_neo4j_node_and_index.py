from neo4j import GraphDatabase


def clear_database(uri, username, password):
    try:
        # 建立连接
        driver = GraphDatabase.driver(uri, auth=(username, password))

        with driver.session() as session:
            # 删除所有节点和关系
            session.run("MATCH (n) DETACH DELETE n")

            # 获取所有索引名称并删除
            index_results = session.run("SHOW INDEXES")
            indexes = [record["name"] for record in index_results]
            for index_name in indexes:
                session.run(f"DROP INDEX {index_name}")

            # 获取所有约束名称并删除
            constraint_results = session.run("SHOW CONSTRAINTS")
            constraints = [record["name"] for record in constraint_results]
            for constraint_name in constraints:
                session.run(f"DROP CONSTRAINT {constraint_name}")

        print("数据库清理完成！")

    except Exception as e:
        print(f"发生错误：{str(e)}")

    finally:
        # 关闭连接
        driver.close()


# 使用示例
uri = "neo4j://localhost:7687"
username = "neo4j"
password = "12345678"

clear_database(uri, username, password)
print('done')