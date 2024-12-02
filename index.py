import os
from math import ceil
from urllib.parse import quote

# 配置目录和文件
html_directory = "/opt/1panel/apps/openresty/openresty/www/sites/reader.colors.nyc.mn/index/"  # HTML 文件所在的目录
output_directory = "/opt/1panel/apps/openresty/openresty/www/sites/reader.colors.nyc.mn/index/"  # 输出的 HTML 文件目录
index_output_file = "/opt/1panel/apps/openresty/openresty/www/sites/reader.colors.nyc.mn/index/index.html"  # 生成的主 index.html 文件
links_per_page = 15  # 每页显示的链接数
base_url = "https://reader.colors.nyc.mn/"  # 基本的 URL


# 获取 HTML 文件的链接
def get_html_files():
    links = []
    for root, _, files in os.walk(html_directory):
        for file_name in files:
            if file_name.endswith(".html"):
                file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_path, html_directory).replace("\\", "/")
                # 对链接中的汉字进行编码
                encoded_path = quote(relative_path)
                url = os.path.join(base_url, encoded_path)
                links.append((file_name, url))  # 保存文件名和对应链接
    return links


# 生成带分页的 index.html 文件
def generate_index_html(links):
    os.makedirs(output_directory, exist_ok=True)

    # 计算分页
    total_links = len(links)
    total_pages = ceil(total_links / links_per_page)

    # 创建分页的 HTML 文件
    for page in range(1, total_pages + 1):
        page_file = os.path.join(output_directory, f"index_page_{page}.html")
        with open(page_file, "w", encoding="utf-8") as f:
            f.write(f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>听书网_有声小说网_免费听书_有声读物_听书楼</title>
    <meta name="keywords" content="免费听书,有声小说,听书网,在线评书,有声读物,听书楼"/>
    <meta name="description" content="听书楼在线听书网提供最新最全热门有声小说,有声读物,评书有声小说每日更新,支持自动连播,无弹窗,听书楼在线听书网为你释放双眼，用耳朵享受阅读的乐趣!"/>
    <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=0.5, maximum-scale=1, user-scalable=no">
    <meta http-equiv="content-language" content="zh-cn">
    <meta name="applicable-device" content="mobile">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="container mt-5">
    <h1 class="text-center mb-4">听书楼</h1>
    <form class="mb-4" action="https://www.bing.com/search" method="get">
        <div class="input-group">
            <input type="hidden" name="q" value="site:reader.colors.nyc.mn">
            <input type="text" class="form-control" name="q" placeholder="搜索听书内容..." aria-label="搜索听书内容">
            <button class="btn btn-primary" type="submit">搜索</button>
        </div>
    </form>
    <ul class="list-group">
""")

            # 分页内容
            start_index = (page - 1) * links_per_page
            end_index = min(start_index + links_per_page, total_links)
            for file_name, link in links[start_index:end_index]:
                # 提取文件名作为标题
                file_name_without_extension = os.path.splitext(file_name)[0]
                f.write(f'<li class="list-group-item"><a href="{link}" target="_blank">{file_name_without_extension}</a></li>\n')

            f.write("""
    </ul>
    <nav class="mt-4">
        <ul class="pagination justify-content-center">
""")

            # 分页导航：只展示数字链接，不展示所有分页
            if page > 1:
                f.write(f'<li class="page-item"><a class="page-link" href="index_page_{page-1}.html">上一页</a></li>\n')

            for p in range(1, total_pages + 1):
                if p == page:
                    f.write(f'<li class="page-item active"><span class="page-link">{p}</span></li>\n')
                elif abs(p - page) <= 2:
                    f.write(f'<li class="page-item"><a class="page-link" href="index_page_{p}.html">{p}</a></li>\n')

            if page < total_pages:
                f.write(f'<li class="page-item"><a class="page-link" href="index_page_{page+1}.html">下一页</a></li>\n')

            f.write("""
        </ul>
    </nav>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

    # 生成主 index.html 指向第一页
    with open(index_output_file, "w", encoding="utf-8") as f:
        f.write('<html><head><meta http-equiv="refresh" content="0; URL=index_page_1.html"></head><body></body></html>\n')
    print(f"Index HTML pages saved to {output_directory}")


# 获取 HTML 文件链接并生成页面
links = get_html_files()
generate_index_html(links)
