from flask import render_template, flash, \
                  redirect, abort, \
                  request, url_for
from sqlalchemy.sql import func
from werkzeug.contrib.atom import AtomFeed
from flask_admin.contrib.sqla import ModelView

from hikeblog import app, db, admin
from hikeblog.forms import CreatePostForm, CommentForm,\
                           EditPostForm 
from hikeblog.model import Post, Comment, Tag


POSTS_PER_PAGE = 5

# Register views for Flask-Admin
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Comment, db.session))
admin.add_view(ModelView(Tag, db.session))


@app.route('/recent.atom')
def recent_feed():
    feed = AtomFeed('Recent Posts',
                    feed_url=request.url, 
                    url=request.url_root)
    posts = Post.query.order_by(Post.pub_date.desc()) \
                      .limit(5).all()
    for post in posts:
        feed.add(post.title, post.body,
                 content_type='html',
                 author="Admin",
                 url=url_for('view_post', post_id=post.id),
                 updated=post.pub_date,
                 published=post.pub_date)
    return feed.get_response()


@app.route("/page/<int:page>")
@app.route("/posts")
@app.route("/posts/")
@app.route("/")
def mainpage(page=1):
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1

    posts = Post.query \
                .order_by(Post.pub_date.desc()) \
                .offset((page_number - 1) * POSTS_PER_PAGE)\
                .limit(POSTS_PER_PAGE)
    
    pagination_query = Post.query.paginate(page_number, POSTS_PER_PAGE)

    """
    tags = Tag.query \
              .order_by(Tag.name) \
              .limit(10)
    """

    tags_query = db.session.query(Tag.name, func.count(Tag.id).label('tagged_count')) \
                           .join(Tag.posts) \
                           .group_by(Tag.name) \
                           .order_by('tagged_count desc')
                    
    month_query = db.session.query(Post.pub_date, func.count().label('posts_count')) \
                            .group_by(func.strftime('%Y', Post.pub_date),
                                      func.strftime('%m', Post.pub_date)) \
                            .order_by(Post.pub_date.desc()) \
                            .limit(12)

    return render_template('main_page.html', posts=posts, tags=tags_query,
                           months=month_query, pagination=pagination_query)


@app.route("/posts/new", methods=['GET', 'POST'])
def create_post():
    form = CreatePostForm() 
    form.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by('name').all()]
    if form.validate_on_submit():
            
        new_post = Post()
        
        print(form.tags.data)
        
        tags_choices = form.tags.data 
        form.tags.data = []
                
        form.populate_obj(new_post)
        
        for tag_id in tags_choices:
            tag = Tag.query.get(tag_id)
            new_post.tags.append(tag)
        
        db.session.add(new_post)
        db.session.commit()
        
        flash('Post created!', 'alert-success')
        return redirect('/')
    return render_template('new_post.html', form=form)


@app.route("/posts/<int:post_id>", methods=['GET', 'POST'])
def view_post(post_id):
    try:
        post = Post.query.get(post_id)
        if post is None:  # or post.deleted:
            abort(404)
    except OverflowError:
        abort(404)
        
    comments = post.comments.all()
    
    print(post.pub_date.strftime('%d-%m-%Y'))
    
    post.views += 1
    db.session.add(post)
    db.session.commit()
    
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        form.populate_obj(new_comment)
        
        new_comment.post_id = post.id
        
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment published!', 'success')
    return render_template('post.html', post=post, comments=comments,
                           form=form)


@app.route("/posts/<int:post_id>/edit", methods=['GET', 'POST'])
def edit_post(post_id):
    try:
        post = Post.query.get(post_id)
        if post is None:  # or post.deleted:
            abort(404)
    except OverflowError:
        abort(404)
    form = EditPostForm(obj=post)
    if request.method == 'POST' and form.validate_on_submit():
        tags_choices = form.tags.data
        form.tags.data = []
        form.populate_obj(post)     
        for tag_name in tags_choices:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag is None:
                tag = Tag()
                tag.name = tag_name
            post.tags.append(tag)
        
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("view_post", post_id=post.id))
    selected_tags = [tag.name for tag in post.tags]
    # print(selected_tags)

    form.tags.data = selected_tags
    form.tags.choices = [(tag.name, tag.name) for tag in Tag.query \
                                                            .order_by('name') \
                                                            .all()]

    return render_template('new_post.html', form=form)


@app.route("/tag/<tag_name>")
@app.route("/tag/<tag_name>/")
@app.route("/tag/<tag_name>/page/<int:page>")
def view_tagged_post(tag_name, page=1):
    tag = Tag.query.filter_by(name=tag_name).first()
    if tag is None:
        abort(404)
        
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
        
    tagged_posts = tag.posts \
        .order_by(Post.pub_date.desc()) \
        .offset((page_number - 1) * POSTS_PER_PAGE) \
        .limit(POSTS_PER_PAGE)

    if not tagged_posts:
        abort(404)      

    pagination_query = tag.posts \
        .order_by(Post.pub_date.desc()) \
        .paginate(page, POSTS_PER_PAGE)
        
    tags = Tag.query.order_by(Tag.name).limit(10)
    
    return render_template('tagged_posts.html', posts=tagged_posts,
                            tags=tags, pagination=pagination_query,
                            tag_name=tag_name)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error=error), 404


@app.template_filter('datetime')
def datetime_filter(value, format="%d-%m-%Y"):
    return value.strftime(format)