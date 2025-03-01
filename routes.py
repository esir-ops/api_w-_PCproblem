from flask import Flask, request, jsonify
from database import db
from models import TriviaQuestion, User, Score, Feedback, Notification
from config import Config
import random

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# ✅ Create a new trivia question (POST)
@app.route('/trivia/questions', methods=['POST'])
def add_question():
    data = request.json
    new_question = TriviaQuestion(
        category=data['category'],
        question=data['question'],
        answer=data['answer'],
        difficulty=data['difficulty']
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'Question added successfully'}), 201

# ✅ Retrieve all trivia questions (GET)
@app.route('/trivia/questions', methods=['GET'])
def get_questions():
    questions = TriviaQuestion.query.all()
    return jsonify([{'id': q.id, 'question': q.question, 'category': q.category, 'answer': q.answer} for q in questions])

# ✅ Update a trivia question (PUT)
@app.route('/trivia/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    data = request.json
    question = TriviaQuestion.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    question.question = data.get('question', question.question)
    question.answer = data.get('answer', question.answer)
    db.session.commit()
    return jsonify({'message': 'Question updated successfully'})

# ✅ Delete a trivia question (DELETE)
@app.route('/trivia/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = TriviaQuestion.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Question deleted successfully'})

# ✅ Retrieve all trivia categories (GET)
@app.route('/trivia/categories', methods=['GET'])
def get_categories():
    categories = ["Science", "History", "Sports", "Entertainment", "Geography"]
    return jsonify({"categories": categories})

# ✅ Get a random trivia question (GET)
@app.route('/trivia/questions/random', methods=['GET'])
def get_random_question():
    questions = TriviaQuestion.query.all()
    if not questions:
        return jsonify({'message': 'No questions available'}), 404
    question = random.choice(questions)
    return jsonify({
        'id': question.id,
        'category': question.category,
        'question': question.question,
        'answer': question.answer,
        'difficulty': question.difficulty
    })

# ✅ Get a random trivia question from a specific category (GET)
@app.route('/trivia/questions/<string:category>/random', methods=['GET'])
def get_random_question_by_category(category):
    questions = TriviaQuestion.query.filter_by(category=category).all()
    if not questions:
        return jsonify({'message': 'No questions available in this category'}), 404
    question = random.choice(questions)
    return jsonify({
        'id': question.id,
        'category': question.category,
        'question': question.question,
        'answer': question.answer,
        'difficulty': question.difficulty
    })

# ✅ Get the correct answer for a trivia question (GET)
@app.route('/trivia/questions/<int:question_id>/answer', methods=['GET'])
def get_answer(question_id):
    question = TriviaQuestion.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    return jsonify({'question': question.question, 'correct_answer': question.answer})

# ✅ Get hints for a trivia question (GET)
@app.route('/trivia/questions/<int:question_id>/hints', methods=['GET'])
def get_hints(question_id):
    question = TriviaQuestion.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    hint = f"The answer starts with '{question.answer[0]}' and ends with '{question.answer[-1]}'"
    return jsonify({'question': question.question, 'hint': hint})

# ✅ Get leaderboard (GET)
@app.route('/trivia/leaderboard', methods=['GET'])
def get_leaderboard():
    top_users = User.query.order_by(User.score.desc()).limit(10).all()
    return jsonify([{'username': u.username, 'score': u.score} for u in top_users])

# ✅ Get user score history (GET)
@app.route('/trivia/score/<int:user_id>', methods=['GET'])
def get_user_score(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'username': user.username, 'score': user.score})

# ✅ Update user score (PUT)
@app.route('/trivia/score/update', methods=['PUT'])
def update_score():
    data = request.json
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.score += data['points']
    db.session.commit()
    return jsonify({'message': 'Score updated successfully'})

# ✅ Get quiz history (GET)
@app.route('/trivia/user/<int:user_id>/history', methods=['GET'])
def get_user_history(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'username': user.username, 'history': 'Past quiz history will be added here'})

# ✅ Submit feedback (POST)
@app.route('/trivia/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    feedback = Feedback(user_id=data['user_id'], question_id=data['question_id'], comment=data['comment'])
    db.session.add(feedback)
    db.session.commit()
    return jsonify({'message': 'Feedback submitted successfully'}), 201

# ✅ Get quiz recommendations (GET)
@app.route('/trivia/quiz/recommendations', methods=['GET'])
def get_recommendations():
    return jsonify({'message': 'Recommended categories based on user preferences will be added here'})

# ✅ Manage notifications (POST, DELETE)
@app.route('/trivia/notifications', methods=['POST'])
def add_notification():
    data = request.json
    notification = Notification(user_id=data['user_id'], message=data['message'])
    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': 'Notification added successfully'}), 201

@app.route('/trivia/notifications/<int:user_id>', methods=['DELETE'])
def delete_notification(user_id):
    notifications = Notification.query.filter_by(user_id=user_id).all()
    for notif in notifications:
        db.session.delete(notif)
    db.session.commit()
    return jsonify({'message': 'Notifications deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)