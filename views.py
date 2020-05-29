from datetime import datetime
from .database import db
from .app import app
from flask import Flask, render_template, request, redirect, session, url_for
from .models import User, Signin, Problem, Idea, Comment, Logindate
import os

# where do you want to trnsfer the picture
app.config["IMAGE_UPLOADS"] = 'static/images'

#route <---routing
#index/home route
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        signup = Signin(uname=request.form['username'], password=request.form['pass'], status="U")
        tmp = Signin.query.filter_by(uname = request.form['username']).first()
        # tmp1 = request.form['username']
        # tmp2 = request.form['pass']
        # print(tmp1, tmp2)
        if tmp:
            session['msg'] = "Username already existed."
            return redirect('/')
        # elif tmp1 is None or tmp2 is None:
        #     session['msg'] = "Insert your username and password."
        #     return redirect('/')
        else:
            try:
                db.session.add(signup)
                db.session.commit()
                db.session.refresh(signup)
                user = User(signin_id=signup.id, name=request.form['name'], major=request.form['major'], avator="avator.jpg")
                db.session.add(user)
                db.session.commit()
                session['id'] = signup.id
                l_date = Logindate(logindate = datetime.now(), signin_id = signup.id)
                db.session.add(l_date)
                db.session.commit()
                return redirect('/timeline')
            except:
                return 'Error'
    else:
        if session.get('msg') is not None:
            msg = session['msg']
            return render_template('index.html', msg = msg)
        else:
            return render_template('index.html', msg= '')


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'POST':
        signin = Signin.query.filter_by(uname=request.form['username'], password=request.form['pass']).first()
        if signin:
            session['id'] = signin.id
            if signin.status == "U":
                try:
                    l_date = Logindate(logindate = datetime.now(), signin_id = signin.id)
                    db.session.add(l_date)
                    db.session.commit()
                    return redirect('/timeline')
                except:
                    return 'Error in SIGNIN'
            else:
                return redirect('/activity')
        else:
            return 'Error in SIGNIN'
    else:
        return render_template('index.html')


@app.route('/submission', methods=['POST','GET'])
def submission():
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        if request.method == 'POST':
            sub = Problem(p_title=request.form['p_title'], p_main=request.form['p_main'], u_id=user_id)
            try:
                db.session.add(sub)
                db.session.commit()
                return redirect('/timeline')
            except:
                return 'Error in SUBMISSION'
        else:
            return render_template('submission.html', user=user, signin=signin)
    else:
        return redirect('/')


@app.route('/timeline')
def timeline():
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        problem = Problem.query.join(User, Problem.u_id == User.id).join(Signin, User.signin_id == Signin.id).add_columns(Problem.id, Problem.p_title, Problem.p_main, Problem.u_id, User.avator, Signin.uname).order_by(Problem.id.desc())

        return render_template('timeline.html', user=user, signin=signin, problem=problem)
    else:
        return render_template('index.html')


@app.route('/editProf', methods=['POST', 'GET'])
def editProf():
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        if request.method == 'POST':
            signin.uname = request.form['uname']
            signin.password = request.form['password']
            # user.avator = request.form['avator']
            # if 'avator' not in request.files and signin.uname != '' and signin.password != '':
            if not request.files['avator']:
                try:
                    db.session.commit()
                    return redirect('/timeline')
                except:
                    return 'Error in editing profile'
            elif signin.uname =='' and signin.password == '' and request.files:
                user.avator = request.files['avator']
                try:
                    db.session.commit()
                    return redirect('/timeline')
                except:
                    return 'Error in editing avator'
            else:
                images = request.files['avator']
                user.avator = images.filename
                images.save(os.path.join(app.config["IMAGE_UPLOADS"], images.filename))
                try:
                    db.session.commit()
                    return redirect('/timeline')
                except:
                    return 'Error in editing profile and avator'
        else:
            return render_template('editprof.html', signin = signin, user=user)
    else:
        return redirect('/')


@app.route('/submitidea/<int:id>', methods=['POST', 'GET'])
def submitidea(id):
    #problem = Problem.query.filter_by(id=).first()
    if 'id' in session:
        #FOR SHOW SCREEN
        problem = Problem.query.get(id)
        idea = Idea.query.join(User, Idea.u_id == User.id).join(Signin, User.signin_id == Signin.id).add_columns(Idea.id, Idea.idea, Idea.p_id, Idea.u_id, Signin.uname).filter(Idea.p_id==id).order_by(Idea.id.desc())
        comment = Comment.query.join(User, Comment.u_id == User.id).join(Signin, User.signin_id == Signin.id).add_columns(Comment.id, Comment.comment, Comment.p_id, Comment.u_id, Comment.i_id, Signin.uname).filter(Comment.p_id==id).order_by(Comment.id.desc())
        #FOR INPUT FORM
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        if request.method == 'POST':
            i = Idea(idea=request.form['idea'], u_id=user_id, p_id=id)
            try:
                db.session.add(i)
                db.session.commit()
                return render_template('submitidea.html', signin = signin, user=user, problem=problem, idea=idea, comment=comment)
            except:
                return 'Error in SUBMISSION'
        else:
            return render_template('submitidea.html', signin = signin, user=user, problem=problem, idea=idea, comment=comment)
    else:
        return redirect('/')


@app.route('/submitcomment/<int:i_id>/<int:p_id>',methods=['POST', 'GET'])
def sbumitcomment(i_id, p_id):
    if 'id' in session:
        idea = Idea.query.get(i_id)
        comment = Comment.query.filter_by(i_id=i_id)
        problem = Problem.query.get(p_id)

        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        if request.method == 'POST':
            c = Comment(comment=request.form['comment'], u_id=user_id, i_id=i_id, p_id=p_id)
            try:
                db.session.add(c)
                db.session.commit()
                # comment = Comment.query.filter_by(i_id=i_id)
                # return redirect('/submitidea/<int:p_id>')
                return redirect(url_for('submitidea', id=p_id))
                # return render_template('submitidea.html', signin=signin, user=user, problem=problem, idea=idea, comment=comment)
            except:
                return 'Error in SUBMISSION'
        else:
            return render_template('submitidea.html', signin=signin, user=user, problem=problem, idea=idea, comment=comment)
    else:
        return redirect('/')


@app.route('/myaccount/<int:id>', methods=['POST', 'GET'])
def myaccount(id):
    if 'id' in session:
        #FOR SHOW SCREEN
        problem = Problem.query.filter_by(u_id=id).order_by(Problem.id.desc())
        idea = Idea.query.join(Problem, Idea.p_id == Problem.id).add_columns(Idea.id, Idea.idea, Idea.p_id, Idea.u_id, Problem.p_title).filter(Idea.u_id == id).order_by(Idea.id.desc())
        comment = Comment.query.join(Idea, Comment.i_id == Idea.id).join(Problem, Comment.p_id == Problem.id).add_columns(Comment.id, Comment.p_id, Comment.u_id, Comment.i_id, Comment.comment, Idea.idea, Problem.p_title).filter(Comment.u_id == id).order_by(Comment.id.desc())
        account = User.query.join(Signin, User.signin_id == Signin.id).add_columns(User.id, User.avator, User.major, Signin.uname).filter(User.id == id).first()
        #FOR INPUT FORM
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        return render_template('myaccount.html', problem=problem, idea=idea, comment=comment, account=account, signin=signin, user=user)


@app.route('/searchresult', methods=['POST', 'GET'])
def searchresult():
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        tag = request.form["tag"]
        search = "%{}%".format(tag)
        posts = Problem.query.join(User, Problem.u_id == User.id).join(Signin, User.signin_id == Signin.id).add_columns(Problem.id, Problem.p_title, Problem.p_main, Problem.u_id, User.avator, Signin.uname).filter(Problem.p_title.like(search)).order_by(Problem.id.desc()).all()
        return render_template('searchresult.html', user=user, signin=signin, posts=posts)
    else:
        return redirect('/timeline')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/ski')
def ski():
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        return render_template('ski.html',user=user, signin=signin)
    else:
        return redirect('/')
        

@app.route('/activity')
def activity():
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        return render_template('activity.html',user=user, signin=signin)
    else:
        return redirect('/')
        
@app.route('/check_p')
def check_p():
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        problem = Problem.query.join(User, Problem.u_id == User.id).join(Signin, User.signin_id == Signin.id).add_columns(Problem.id, Problem.p_title, Problem.p_main, Problem.u_id, User.avator, Signin.uname).order_by(Problem.id.desc())
        return render_template('check_p.html',user=user, signin=signin, problem=problem)
    else:
        return redirect('/')

@app.route('/check_i')
def check_i():
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        idea = Idea.query.join(User, Idea.u_id == User.id).join(Signin, User.signin_id == Signin.id).add_columns(Idea.id, Idea.idea, Idea.p_id, Idea.u_id, User.avator, Signin.uname).order_by(Idea.id.desc()).all()
        return render_template('check_i.html',user=user, signin=signin, idea=idea)
    else:
        return redirect('/')

@app.route('/check_c')
def check_c():
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        comment = Comment.query.join(User, Comment.u_id == User.id).join(Signin, User.signin_id == Signin.id).add_columns(Comment.id, Comment.i_id, Comment.u_id, Comment.comment, User.avator, Signin.uname).order_by(Comment.id.desc()).all()
        return render_template('/check_c.html',user=user, signin=signin, comment=comment)
    else:
        return redirect('/')

@app.route('/check_u')
def check_u():
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        # session.query().filter_by(condition).count()
        imfo = User.query.join(Signin, User.signin_id == Signin.id).add_columns(User.id, User.name, User.major, User.avator, Signin.uname).order_by(User.id.desc()).all()
        return render_template('check_u.html',user=user, signin=signin, imfo=imfo)
    else:
        return redirect('/')

@app.route('/userAct/<int:u_id>')
def userAct(u_id):
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        time_count = Logindate.query.filter_by(signin_id=u_id).count()
        time_problem = Problem.query.filter_by(u_id=u_id).count()
        time_idea = Idea.query.filter_by(u_id=u_id).count()
        time_comment = Comment.query.filter_by(u_id=u_id).count()
        user_imfo = User.query.join(Signin, User.signin_id==Signin.id).add_columns(User.id, User.avator, User.major, Signin.uname).filter(User.id==u_id).first()
        return render_template('userAct.html', user=user, signin=signin, tc=time_count, tp=time_problem, ti=time_idea, tcm=time_comment, ui=user_imfo)


@app.route('/logindate/<int:u_id>')
def logindate(u_id):
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        history_login = Logindate.query.filter_by(signin_id=u_id).order_by(Logindate.id.desc()).all()
        user_imfo = User.query.join(Signin, User.signin_id==Signin.id).add_columns(User.id, User.avator, User.major, Signin.uname).filter(User.id==u_id).first()
        return render_template('userLogin.html', user=user, signin=signin, hl=history_login, ui=user_imfo)


@app.route('/s_problem/<int:u_id>')
def s_problem(u_id):
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        user_imfo = User.query.join(Signin, User.signin_id==Signin.id).add_columns(User.id, User.avator, User.major, Signin.uname).filter(User.id==u_id).first()
        prob_imfo = Problem.query.filter_by(u_id=u_id).order_by(Problem.id.desc()).all()
        return render_template('s_problem.html', user=user, signin=signin, ui=user_imfo, pi=prob_imfo)


@app.route('/s_idea/<int:u_id>')
def s_idea(u_id):
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        user_imfo = User.query.join(Signin, User.signin_id==Signin.id).add_columns(User.id, User.avator, User.major, Signin.uname).filter(User.id==u_id).first()
        idea_imfo = Idea.query.filter_by(u_id=u_id).order_by(Idea.id.desc()).all()
        return render_template('s_idea.html', user=user, signin=signin, ui=user_imfo, ii=idea_imfo)


@app.route('/s_comment/<int:u_id>')
def s_comment(u_id):
    if 'id' in session:
        user_id = session['id']
        user = User.query.filter_by(signin_id=user_id).first()
        signin = Signin.query.filter_by(id=user_id).first()
        user_imfo = User.query.join(Signin, User.signin_id==Signin.id).add_columns(User.id, User.avator, User.major, Signin.uname).filter(User.id==u_id).first()
        comment_imfo = Comment.query.filter_by(u_id=u_id).order_by(Comment.id.desc()).all()
        return render_template('s_comment.html', user=user, signin=signin, ui=user_imfo, ci=comment_imfo)



# from flask import  make_response
# from io import BytesIO
# import urllib
# from matplotlib.backends.backend_agg import FigureCanvasAgg
# from matplotlib.figure import Figure
# import matplotlib.pyplot as plt
# import random
# import numpy as np

# fig = plt.figure()
# ax = fig.add_subplot()

# x = np.arange(0,100,0.1)
# y = x**2

# @app.route('/plot')
# def plot():
#     plt.cla()

#     plt.title('Graph')
#     plt.legend()
#     plt.grid()
#     plt.xlabel('x')
#     plt.ylabel('y')
#     plt.plot(x, y)

#     canvas = FigureCanvasAgg(fig)
#     png_output = BytesIO()
#     canvas.print_png(png_output)
#     data = png_output.getvalue()

#     response = make_response(data)
#     response.headers['Content-Type'] = 'image/png'
#     return render_template('plot.html', r=response)