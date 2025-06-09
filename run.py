from flaskblog import create_app
from flaskblog.users.utils import status_emojis

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

@app.context_processor
def inject_status_emojis():
    return dict(status_emojis=status_emojis)