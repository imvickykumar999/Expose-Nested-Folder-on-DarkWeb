from flask import Flask, render_template_string, send_from_directory, abort, request
import os

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.getcwd())

HTML = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium File Browser</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', sans-serif;
        }

        body {
            min-height: 100vh;
            background: linear-gradient(135deg, #0f172a, #1e293b, #334155);
            padding: 40px;
            color: white;
        }

        .container {
            max-width: 1100px;
            margin: auto;
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(18px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 24px;
            padding: 35px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
        }

        .toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 25px;
        }

        h2 {
            font-size: 30px;
            font-weight: 700;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }

        h2 a {
            text-decoration: none;
            color: #38bdf8;
            transition: .25s;
        }

        h2 a:hover {
            color: #facc15;
        }

        .path-separator {
            color: #94a3b8;
        }

        .sort-btn {
            padding: 12px 18px;
            border: none;
            border-radius: 14px;
            background: #38bdf8;
            color: #0f172a;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            transition: .3s;
        }

        .sort-btn:hover {
            background: #facc15;
            transform: translateY(-2px);
        }

        .grid {
            display: grid;
            gap: 14px;
        }

        .item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 18px 22px;
            border-radius: 18px;
            text-decoration: none;
            color: white;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: .3s;
        }

        .item:hover {
            transform: translateY(-3px);
            background: rgba(56, 189, 248, 0.15);
            border-color: #38bdf8;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
        }

        .left {
            display: flex;
            align-items: center;
            gap: 14px;
            font-size: 18px;
        }

        .icon {
            font-size: 24px;
        }

        .badge {
            font-size: 13px;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.1);
            color: #cbd5e1;
        }

        .back {
            display: inline-block;
            margin-bottom: 18px;
            color: white;
            text-decoration: none;
            padding: 12px 18px;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.08);
        }

        .back:hover {
            background: rgba(255, 255, 255, 0.14);
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="toolbar">
            <h2>
                📂 <a href="/browse/">Home</a>
                {% set parts = current_path.split('/') if current_path else [] %}
                {% set ns = namespace(path='') %}
                {% for part in parts %}
                {% set ns.path = ns.path + '/' + part if ns.path else part %}
                <span class="path-separator">/</span>
                <a href="/browse/{{ ns.path }}">{{ part }}</a>
                {% endfor %}
            </h2>
            <a class="sort-btn" href="?sort={{ 'desc' if sort=='asc' else 'asc' }}">Sort {{ '↓' if sort=='asc' else '↑'
                }}</a>
        </div>
        {% if parent %}<a class="back" href="/browse/{{ parent }}">⬅ Back</a>{% endif %}
        <div class="grid">
            {% for item in items %}
            <a class="item" href="{{ '/browse/' + item.path if item.is_dir else '/file/' + item.path }}" {% if not
                item.is_dir %}target="_blank" {% endif %}>
                <div class="left"><span class="icon">{{ '📁' if item.is_dir else item.icon }}</span><span>{{ item.name
                        }}</span></div>
                <span class="badge">{{ 'Folder' if item.is_dir else item.ext }}</span>
            </a>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

def get_icon(filename):
    ext = filename.lower().split('.')[-1]
    if ext in ['mp4','mkv','avi']: return '🎬', ext.upper()
    if ext in ['html','htm']: return '🌐', ext.upper()
    if ext in ['pdf']: return '📕', ext.upper()
    return '📄', ext.upper()

@app.route('/')
def home():
    return browse('')

@app.route('/browse/<path:subpath>')
@app.route('/browse/', defaults={'subpath': ''})
def browse(subpath):
    full_path = os.path.join(BASE_DIR, subpath)
    if not os.path.exists(full_path): abort(404)

    sort_order = request.args.get('sort', 'asc')
    names = os.listdir(full_path)
    names = sorted(names, reverse=(sort_order=='desc'))

    items=[]
    for name in names:
        item_path=os.path.join(full_path,name)
        rel=os.path.relpath(item_path,BASE_DIR).replace('\\','/')
        icon,ext=get_icon(name)
        items.append({'name':name,'path':rel,'is_dir':os.path.isdir(item_path),'icon':icon,'ext':ext})

    parent=os.path.dirname(subpath).replace('\\','/') if subpath else None
    return render_template_string(HTML,items=items,current_path=subpath,parent=parent,sort=sort_order)

@app.route('/file/<path:filepath>')
def file(filepath):
    full_path=os.path.join(BASE_DIR,filepath)
    if not os.path.exists(full_path): abort(404)
    return send_from_directory(os.path.dirname(full_path),os.path.basename(full_path))

if __name__=='__main__':
    app.run(port=8000,debug=False)
