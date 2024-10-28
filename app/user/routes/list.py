import json

from flask import request, jsonify, current_app

from app import db
from app.user.routes import user_blueprint
from compliance_lib_schemas.models import User
# from helpers.token import TokenManager
from sqlalchemy.sql import text
from operator import itemgetter
from sqlalchemy import asc, desc


@user_blueprint.route("", methods=["GET"])
def list_users():
    
    db_session = db.session()
    # token_manager = TokenManager()
    sort = request.args.get('sort', None)
    filters = request.args.getlist('filter')
    continuation_token = request.args.get('cursor', None)
    max_keys = request.args.get('max_keys', 1000)
    
    query = db_session.query(User)
    
    current_app.logger.info(filters)

    if filters:
        for filter in filters:
            filter = json.loads(filter)
            column, operator, value = itemgetter('column', 'operator', 'value')(filter)
            if operator == "like":
                query = query.filter(getattr(User, column).like(f'%{value}%'))
            if operator == "equals":
                query = query.filter(getattr(User, column) == value)
    
    if sort:
        sort = json.loads(sort)
        column, operator, value = itemgetter('column', 'operator', 'value')(sort)
        sort_direction = desc if value == "desc" else asc
        
        query = query.order_by(sort_direction(getattr(User, column)))
    else:
        query = query.order_by(User.fullname.asc())
        
    # if continuation_token:
    #     continuation_token_decoded = json.loads(token_manager.decode(continuation_token))
    #     min_id = continuation_token_decoded["min_id"]
    #     max_id = continuation_token_decoded["max_id"]
    #     query = query.filter(User.id > max_id)
        
    # finally limit it by max keys
    query = query.limit(max_keys)
    
    users = query.all()
    
    users = [i.serialize for i in users]
    
    # if not users:
    #     next_continuation_token = None
    #     is_truncated = False
    # else:
    #     max_id = max(users, key=lambda x:x['id'])["id"]
    #     min_id = min(users, key=lambda x:x['id'])["id"]
        
    #     next_continuation_token = token_manager.encode(
    #         json.dumps({
    #             "min_id": min_id,
    #             "max_id": max_id
    #         })
    #     )
    #     is_truncated = True
    
    response = {
        # "metadata": {
        #     "continuation_token": continuation_token,
        #     "next_continuation_token": next_continuation_token,
        #     "max_keys": max_keys,
        #     "is_truncated": is_truncated
        # },
        "users": users
    }
    
    return jsonify(response), 200