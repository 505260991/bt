# bt

一个基于 FastAPI 的影视搜索服务，提供：
- `/search`：搜索影片
- `/detail`：获取影片磁力资源
- `/img`：图片代理
- `/`：内置前端页面（`index.html`）

## 本地运行

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

打开：`http://127.0.0.1:8000`

## Docker 部署

### 1) 构建镜像

```bash
docker build -t bt:latest .
```

### 2) 启动容器

```bash
docker run -d --name bt -p 8000:8000 bt:latest
```

### 3) 访问服务

- 前端页面：`http://127.0.0.1:8000`
- 搜索接口：`http://127.0.0.1:8000/search?q=测试`

### 4) 停止并删除容器

```bash
docker stop bt && docker rm bt
```
