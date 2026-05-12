from flask import Flask, render_template, request, url_for, make_response, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my-secret-key'
db = SQLAlchemy(app)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)


with app.app_context():
    db.create_all()

CATEGORIES = {'Food', 'Transport', 'Rent', 'Utilities', 'Rent', 'Insurance'}


def parse_date_or_none(s: str):
    if not s:
        return  None
    try: 
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


@app.route("/")
def index():

    # 1 read query strings 

    start_str = request.args.get("start" or "").strip()
    end_str = (request.args.get("end") or "").strip()

    # 2 parsing

    start_date = parse_date_or_none(start_str)
    end_date = parse_date_or_none(end_str)

    if start_date and end_date and end_date < start_date:
        flash("End date cannot be before start date", "error")
        start_date = end_date = None
        start_str = end_str = ""

        q= Expense.query

        if start_date:
            q = q.filter(Expense.date >= start_date)
        if end_date:
            q = q.filter(Expense.date<= end_date)
          

    expenses = q.order_by(Expense.date.desc(), Expense.id.desc()).all()
    total = round(sum(e.amount for e in expenses), 2)
    return render_template("index.html", 
                           expenses=expenses, 
                           categories=CATEGORIES,
                           total=total
                           )
    

@app.route("/add", methods=['POST'])
def add():

    description = (request.form.get("description") or  "").strip()
    amount_str = (request.form.get("amount") or  "").strip()
    category = (request.form.get("category") or  "").strip()
    date_str = (request.form.get("date") or  "").strip()

    if not description or not amount_str or not category:
        flash("Please fill Description, amount, and category", "error")
        return redirect(url_for("index"))
    
    try:
        amount = float(amount_str)
        if amount <=0:
            raise ValueError
        
    except ValueError:
        flash("Amount must be a positive number", "error")
        return redirect(url_for("index"))
    
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    
    except ValueError:
        d = date.today()

    
    e = Expense(description=description, amount=amount, category=category, date=d)

    db.session.add(e)
    db.session.commit()

    flash("Expense Added", "Sucess")
    return redirect(url_for("index"))

@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete(expense_id):
        e = Expense.query.get_or_404(expense_id)
        db.session.delete(e)
        db.session.commit()
        flash("Expense deleted", "Sucess")
        return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True, port= 4848)

