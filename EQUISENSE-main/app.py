from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_connection, close_connection
from calculator import run_calculator
from expert_system import run_expert_system
import bcrypt

app = Flask(__name__)
app.secret_key = 'equisense_secret_key'

#  HOME
@app.route('/')
def index():
        session.clear()
        return render_template('index.html')

# ─── REGISTER 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
                         (full_name, email, hashed_password))
            connection.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Email already exists. Please use a different email.', 'danger')
        finally:
            close_connection(connection, cursor)

    return render_template('register.html')

# ─── LOGIN 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        close_connection(connection, cursor)

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['user_id']
            session['full_name'] = user['full_name']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

# ─── DASHBOARD 
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM recommendations WHERE user_id = %s", (session['user_id'],))
    total = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as count FROM recommendations WHERE user_id = %s AND recommendation = 'BUY'", (session['user_id'],))
    buys = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM recommendations WHERE user_id = %s AND recommendation = 'HOLD'", (session['user_id'],))
    holds = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM recommendations WHERE user_id = %s AND recommendation = 'SELL'", (session['user_id'],))
    sells = cursor.fetchone()['count']

    close_connection(connection, cursor)

    return render_template('dashboard.html',
                           full_name=session['full_name'],
                           total=total,
                           buys=buys,
                           holds=holds,
                           sells=sells)

# ─── ANALYZE 
@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            company_name = request.form['company_name']
            share_price = float(request.form['share_price'])
            eps = float(request.form['eps'])
            current_revenue = float(request.form['current_revenue'])
            previous_revenue = float(request.form['previous_revenue'])
            historical_prices = request.form['historical_prices']

            # Run Calculator Module
            indicators = run_calculator(share_price, eps,
                                        current_revenue, previous_revenue,
                                        historical_prices)

            # Run Expert System Engine
            result = run_expert_system(indicators)

            # Save to database
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO stock_inputs
                (user_id, company_name, share_price, eps, current_revenue, previous_revenue, historical_prices)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (session['user_id'], company_name, share_price, eps,
                  current_revenue, previous_revenue, historical_prices))
            input_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO computed_indicators
                (input_id, user_id, pe_ratio, revenue_growth, rsi, macd, signal_line, ma_50, ma_200)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (input_id, session['user_id'],
                  indicators['pe_ratio'], indicators['revenue_growth'],
                  indicators['rsi'], indicators['macd'],
                  indicators['signal_line'], indicators['ma_50'],
                  indicators['ma_200']))
            indicator_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO recommendations
                (user_id, indicator_id, company_name, recommendation, reason)
                VALUES (%s, %s, %s, %s, %s)
            """, (session['user_id'], indicator_id, company_name,
                  result['recommendation'], result['reason']))

            connection.commit()
            close_connection(connection, cursor)

            return render_template('results.html',
                                   company_name=company_name,
                                   indicators=indicators,
                                   result=result)

        except Exception as e:
            flash(f'Error processing data: {str(e)}', 'danger')
            return redirect(url_for('analyze'))

    return render_template('analyze.html')

# ─── HISTORY 
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.company_name, r.recommendation, r.reason, r.created_at,
               i.pe_ratio, i.revenue_growth, i.rsi, i.macd, i.ma_50, i.ma_200
        FROM recommendations r
        JOIN computed_indicators i ON r.indicator_id = i.indicator_id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
    """, (session['user_id'],))

    records = cursor.fetchall()
    close_connection(connection, cursor)

    return render_template('history.html', records=records)

# ─── PROFILE 
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        action = request.form.get('action')

        # ── UPDATE NAME AND EMAIL ──
        if action == 'update_details':
            full_name = request.form['full_name']
            email = request.form['email']
            try:
                cursor.execute("""
                    UPDATE users SET full_name = %s, email = %s
                    WHERE user_id = %s
                """, (full_name, email, session['user_id']))
                connection.commit()
                session['full_name'] = full_name
                flash('Details updated successfully!', 'success')
            except Exception as e:
                flash('Email already in use by another account.', 'danger')

        # ── CHANGE PASSWORD ──
        elif action == 'change_password':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            cursor.execute("SELECT password FROM users WHERE user_id = %s", (session['user_id'],))
            user = cursor.fetchone()

            if not bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
                flash('Current password is incorrect.', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
            elif len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'danger')
            else:
                hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute("""
                    UPDATE users SET password = %s WHERE user_id = %s
                """, (hashed, session['user_id']))
                connection.commit()
                flash('Password changed successfully!', 'success')

        close_connection(connection, cursor)
        return redirect(url_for('profile'))

    # GET — fetch current user details
    cursor.execute("SELECT full_name, email, created_at FROM users WHERE user_id = %s", (session['user_id'],))
    user = cursor.fetchone()
    close_connection(connection, cursor)

    return render_template('profile.html', user=user)

# ─── LOGOUT 
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ─── RUN
if __name__ == '__main__':
    app.run(debug=True)