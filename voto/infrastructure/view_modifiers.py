from functools import wraps
import flask
import werkzeug
import werkzeug.wrappers
# This file mostly copied from TalkPython FM course  on building flask apps
# https://training.talkpython.fm/courses/details/building-data-driven-web-applications-in-python-with-flask-sqlalchemy-and-bootstrap


def response(*, mimetype: str = None, template_file: str = None):
    """ This wrapper of app views defines logic what to do if your view returns a dict or a response when calling a
    template. So functions in the main app just need to return data, not render templates. Standardises passing dicts
    and responses, as there are most reliable data structures to work with
    """

    def response_inner(f):

        @wraps(f)
        def view_method(*args, **kwargs):
            response_val = f(*args, **kwargs)

            if isinstance(response_val, werkzeug.wrappers.Response):
                return response_val

            if isinstance(response_val, flask.Response):
                return response_val

            if isinstance(response_val, dict):
                model = dict(response_val)
            else:
                model = dict()

            if template_file and not isinstance(response_val, dict):
                raise Exception(
                    "Invalid return type {}, we expected a dict as the return value.".format(type(response_val)))

            if template_file:
                response_val = flask.render_template(template_file, **response_val)

            resp = flask.make_response(response_val)
            resp.model = model
            if mimetype:
                resp.mimetype = mimetype

            return resp

        return view_method

    return response_inner
