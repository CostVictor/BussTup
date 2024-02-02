from flask_security import login_required
from flask import Response
from app import app
import time


def extract_info(function_extract):
    def generate_events():
        last_sent = time.time()
        
        while True:
            current_time = time.time()
            elapsed_time = current_time - last_sent

            if elapsed_time >= 3:
                yield function_extract()
                last_sent = current_time
    
    return generate_events()


def extract_agenda():...


def extract_rota():...


'''~~~~~~~~~~~~~~~~~~~~~~~~~'''
''' ~~~~~~~~~ SSE ~~~~~~~~~ '''
'''~~~~~~~~~~~~~~~~~~~~~~~~~'''

@app.route("/stream_agenda")
@login_required
def stream_agenda():
    return Response(extract_info(extract_agenda), mimetype='text/event-stream')


@app.route("/stream_rota")
@login_required
def stream_rota():
    return Response(extract_info(extract_agenda), mimetype='text/event-stream')
