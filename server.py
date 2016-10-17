from flask import Flask, render_template, redirect, request, session, flash
import pg
import markdown
from wiki_linkify import wiki_linkify

app =Flask('Wiki')
db = pg.DB(dbname='Wiki')
app.secret_key = 'best website'

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
    if 'username' in session:
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
    else:
        return render_template(
            'unlogged_edit.html',
            page_name = page_name
        )


@app.route('/<page_name>/save', methods=['POST'])
def submit_edit_page(page_name):
    query = db.query("select * from pages where title = '%s'" %page_name)
    if len(query.namedresult()) == 0:
        db.insert(
            'pages',
            title = page_name
        )
        flash('%s, you have submitted a new Wiki Page'%session['username'])
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
    flash('%s, you have sucessfully edited the page.'%session['username'])
    return redirect('/%s'%page_name)

@app.route('/AllPages')
def render_all_pages():
    query = db.query("select * from pages")
    title_list = query.namedresult()
    return render_template(
        "all_pages.html",
        title_list = title_list
    )

@app.route('/<page_name>/history')
def history_pages(page_name):
    query = db.query("select id from pages where title = '%s'" %page_name)
    pages_id = query.namedresult()[0].id
    page_history = db.query("select * from history where pages_id = '%d' order by date_saved desc" %pages_id).namedresult()
    return render_template(
        "page_history.html",
        page_history = page_history,
        page_name = page_name
    )

@app.route('/<page_name>/history_page', methods=['POST'])
def render_history_page(page_name):
        history_id = int(request.form.get('id'))
        print history_id
        print "BOOOOOOOOOOOM"
        history_content = db.query("select content from history where id = '%d' order by date_saved desc" %history_id).namedresult()[0].content
        history_content = wiki_linkify(history_content)
        history_content = markdown.markdown(history_content)
        return render_template(
            'history_page.html',
            page_name = page_name,
            history_content = history_content
        )

@app.route('/login')
def render_input():
    return render_template(
        "log_in.html"
    )

@app.route('/login/submit', methods=['POST'])
def submit_log_in():
    username = request.form.get('username')
    password = request.form.get('password')
    query = db.query("select * from users where username = '%s'" % username)
    result_list = query.namedresult()
    if len(result_list) > 0:
        user = result_list[0]
        if user.password == password:
            session['username'] = user.username
            flash('You have successfully logged in')
            return redirect('/page_name')
        else:
            return redirect('/login')
    else:
        return redirect('/login')

@app.route('/new_user')
def render_new_user():
    return render_template(
        "create_user.html"
    )

@app.route('/create_user/submit', methods=['POST'])
def submit_new_user():
    username = request.form.get('username')
    password = request.form.get('password')
    query = db.query("select * from users where username = '%s'" % username)
    result_list = query.namedresult()
    if len(result_list) == 0:
        db.insert(
        'users',
        username = username,
        password = password
        )
        flash('You have successfully created a new user')
        return redirect('/login')
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    del session['username']
    flash('You have successfully logged out')
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug = True)
