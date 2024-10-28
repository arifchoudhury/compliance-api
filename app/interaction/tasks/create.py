# from flask import current_app

# from app.extensions import db
# from interaction.forms import CreateInteractionForm
# from compliance_lib_schemas.models import Interaction
# from interaction.exceptions import CreateInteractionFormInvalid

# class CreateInteractionTask:
    
#     def __init__(self, db_session):
#         self.db_session = db_session
    
#     @property
#     def log(self):
#         return current_app.logger
    
#     def get_interaction(self, external_id=None):
        
#         if external_id:
#             interaction = self.db_session.query(Interaction).filter_by(external_id=external_id).first()
#         else:
#             interaction = {}
        
#         return interaction
    
#     def create_interaction(self, external_id, start_time, end_time, withheld, direction, 
#         recorded_phone_number, third_party_phone_number):
        
#         interaction = Interaction(
#             external_id=external_id,
#             start_time=start_time,
#             end_time=end_time,
#             withheld=withheld,
#             direction=direction,
#             recorded_phone_number=recorded_phone_number,
#             third_party_phone_number=third_party_phone_number
#         )
        
#         return interaction
    
#     def update_interaction(self, interaction, external_id, start_time, end_time, withheld, direction, 
#         recorded_phone_number, third_party_phone_number):
        
#         interaction.external_id = external_id
#         interaction.start_time = start_time
#         interaction.end_time = end_time
#         interaction.withheld = withheld
#         interaction.direction = direction
#         interaction.recorded_phone_number = recorded_phone_number
#         interaction.third_party_phone_number = third_party_phone_number
        
        
#     def create(self, external_id, start_time, end_time, withheld, direction, 
#         recorded_phone_number, third_party_phone_number
#     ):
        
#         self.log.info("in interaction create")

                
#         success = False
                
#         form = CreateInteractionForm.from_json(
#             {
#                 "external_id": external_id,
#                 "start_time": start_time,
#                 "end_time": end_time,
#                 "withheld": withheld,
#                 "direction": direction,
#                 "recorded_phone_number": recorded_phone_number.phone_number,
#                 "third_party_phone_number": third_party_phone_number.phone_number
#             }
#         )
        
#         if not form.validate():
#             self.log.critical(f"form is invalid, error: {form.errors}")
#             raise CreateInteractionFormInvalid(f"Interaction form validation failed, error: {form.errors}")
#         else:
#             self.log.info("form is valid")
#             interaction = self.get_interaction(external_id)
#             if interaction:
#                 interaction = self.update_interaction(
#                     interaction,
#                     external_id, start_time, end_time, withheld, direction, 
#                     recorded_phone_number, third_party_phone_number
#                 )
#             else:
#                 interaction = self.create_interaction(
#                     external_id, start_time, end_time, withheld, direction, 
#                     recorded_phone_number, third_party_phone_number
#                 )
#                 self.db_session.add(interaction)
                
#             return interaction
                