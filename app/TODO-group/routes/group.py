# import json

# from flask import request, jsonify, current_app

# from app import db
# from contact.views import recorded_contact_blueprint
# from contact.models import GroupAttributeAssociation, Group, RecordedContactAttribute
# from contact.forms import AddGroupForm

# from auth.decorators import policy_required

# @recorded_contact_blueprint.route("/group", methods=["GET"])
# def get_groups():
    
#     groups_list = []
    
#     groups = db.session.query(Group).all()
    
#     for group in groups:
#         g = group.serialize()
#         groups_list.append(g)
        
#     metadata = {}
#     metadata["columns"] = list(groups_list[0].keys())
#     metadata["searchableColumns"] = metadata["columns"]
    
#     # TODO if groups is null then you'll get no table rows, fix!
        
#     return jsonify({ "metadata": metadata, "groups": groups_list }), 200

# @recorded_contact_blueprint.route("/group/<group_id>", methods=["GET"])
# def get_group(group_id):
    
#     group = db.session.query(Group).filter_by(id=group_id).first()
#     group = group.serialize()
        
#     return jsonify(group), 200

# @recorded_contact_blueprint.route("/group", methods=["POST"])
# def add_group():
    
#     group_info = request.get_json()
    
#     current_app.logger.info(group_info)
    
#     # TODO need to add some validation that atleast 1 value is associated to an attribute rule!
    
#     form = AddGroupForm.from_json(group_info)
        
#     if not form.validate():
#         current_app.logger.info(f"form had errors: {form.errors}")
#         return jsonify({"success": False, "msg": form.errors}), 400
    
#     group = db.session.query(Group).filter_by(name=form.groupName.data).first()
#     if group:
#         return jsonify({"msg": f"Group with name {form.groupName.data} already exists"}), 409
    
#     group = Group(name=form.groupName.data)
    
#     for rule in group_info['rules']:
#         associated_values = group_info['rules'][rule]
#         attribute_name = rule
#         attribute = db.session.query(RecordedContactAttribute).filter_by(
#             name=attribute_name
#         ).first()
        
#         for associated_value in associated_values:
#             group_attribute_association = GroupAttributeAssociation(
#                 group=group,
#                 recorded_contact_attribute_id=attribute.id,
#                 attribute_associated_value=associated_value 
#             )
        
#             db.session.add(group_attribute_association)
        
#     try:
#         db.session.commit()
#         return jsonify({"success": True, "message": "group created"}), 200
#     except Exception as err:
#         db.session.rollback()
#         current_app.logger.critical(f"Failed to create group, error: {err}")
#         return jsonify({"success": False, "msg": f"Oops something went wrong, please try again later: {err}"}), 500
    
        
#     # return jsonify({ "metadata": [], "groups": groups_list }), 200
