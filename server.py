from flask import Flask, render_template, redirect, request
import pg
import markdown
from wiki_linkify import wiki_linkify

app =Flask('Wiki')
db = pg.DB(dbname='Wiki')

@app.route('/')
def render_home():
    return redirect('/HomePage')

@app.route('/<page_name>')
def render_page(page_name):
    query = db.query("select * from pages where title = '%s'" %page_name)
    if len(query.namedresult()) > 0:
        query = query.namedresult()[0]
        pages_id = query.id
        newest_content = db.query("select content from history where pages_id = '%d' order by date_saved desc" %pages_id).namedresult()[0].content
        newest_content = wiki_linkify(newest_content)
        newest_content = markdown.markdown(newest_content)
        return render_template(
            'existing_page.html',
            page_name = page_name,
            newest_content = newest_content
        )
    else:
        return render_template(
        'placeholder.html',
        page_name=page_name
        )

@app.route('/<page_name>/edit')
def render_edit_page(page_name):
    query = db.query("select * from pages where title = '%s'" %page_name)
    if len(query.namedresult()) == 0:
        return render_template(
        'edit_page.html',
        page_name=page_name,
        )
    else:
        query = query.namedresult()[0]
        pages_id = query.id
        newest_content = db.query("select content from history where pages_id = '%d' order by date_saved desc" %pages_id).namedresult()[0].content
        return render_template(
            'edit_page.html',
            page_name = page_name,
            newest_content = newest_content
        )

@app.route('/<page_name>/save', methods=['POST'])
def submit_edit_page(page_name):
    query = db.query("select * from pages where title = '%s'" %page_name)
    if len(query.namedresult()) == 0:
        db.insert(
            'pages',
            title = page_name
        )
    else:
        pass
    content = request.form.get('edits')
    query = db.query("select * from pages where title = '%s'" %page_name)
    query = query.namedresult()[0].id
    db.insert(
        'history',
        content = content,
        pages_id = query
    )
    return redirect('/%s'%page_name)


if __name__ == '__main__':
    app.run(debug = True)
