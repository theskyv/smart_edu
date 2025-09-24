AI智教
生成requirements文件时
https://blog.csdn.net/qq_53644346/article/details/138506229?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522ea8290e3d18c717a0d2847d9d4cd4798%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=ea8290e3d18c717a0d2847d9d4cd4798&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-138506229-null-null.142^v102^pc_search_result_base7&utm_term=%E7%94%9F%E6%88%90requirements.txt%E6%96%87%E4%BB%B6&spm=1018.2226.3001.4187
有三个方法👆csdn链接

#--------------------------------------------------------------------------
https://blog.csdn.net/liaoqingjian/article/details/123703679

①下载pipreqs库，使用以下命令
pip install pipreqs
②使用以下命令生成requirements.txt文件
pipreqs . --encoding=utf8 --force
③生成的requirements.txt文件如下，不会出现所有的python库包
④下载requirements.txt的所有库包的方法命令如下
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple





本地.venv环境测试好之后 构建镜像
docker build -t edu_app:v4  .

创建并运行镜像对应的容器
docker run -d --add-host="host.docker.internal:host-gateway" edu_app:v4

<img width="1480" height="1236" alt="image" src="https://github.com/user-attachments/assets/e74d0048-206e-4b1f-b8de-62f6e07e566d" />


https://blog.csdn.net/weixin_45145684/article/details/144729149
<img width="1488" height="641" alt="image" src="https://github.com/user-attachments/assets/a2b6d2bf-3f11-41dc-b9a3-df146a98f009" />
