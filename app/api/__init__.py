from app.api import chat, lesson, project, question, voice, skill


def register_routes(app):
    app.register_blueprint(chat.bp)
    app.register_blueprint(voice.bp)
    app.register_blueprint(lesson.bp)
    app.register_blueprint(question.bp)
    app.register_blueprint(project.bp)
    app.register_blueprint(skill.bp)
