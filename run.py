from app import app
from app.tasks import sched

if __name__ == "__main__":
  sched.start()
  app.run(debug=True, host="0.0.0.0", port=5000)
