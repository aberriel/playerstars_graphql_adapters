from datetime import datetime
import graphene

class Notification(graphene.ObjectType):
	entity_id = graphene.String()
	player_id = graphene.String()
	status = graphene.String()
	duel_id = graphene.String()
	notification_type = graphene.String()
	notification_image = graphene.String()
	notification_complement = graphene.String()


class CreateNotificationInput(graphene.InputObjectType):
	entity_id = graphene.String(required=True)
	player_id = graphene.String(required=False)
	status = graphene.String(required=False)
	duel_id = graphene.String(required=False)
	notification_type = graphene.String(required=False)
	notification_image = graphene.String(required=False)
	notification_complement = graphene.String(required=False)


class CreateNotification(graphene.Mutation):
	class Arguments:
		input = CreateNotificationInput(required=True)

	entity_id = graphene.String()
	player_id = graphene.String()
	status = graphene.String()
	duel_id = graphene.String()
	notification_type = graphene.String()
	notification_image = graphene.String()
	notification_complement = graphene.String()

	@staticmethod
	def mutate(root, info, notification_data=None):
		entity_id = notification_data.entity_id
		player_id = notification_data.player_id
		status = notification_data.status
		duel_id = notification_data.duel_id
		notification_type = notification_data.notification_type
		notification_image = notification_data.notification_image
		notification_complement = notification_data.notification_complement
		return CreateNotification(
			entity_id=entity_id,
			player_id=player_id,
			status=status,
			duel_id=duel_id,
			notification_type=notification_type,
			notification_image=notification_image,
			notification_complement=notification_complement)


class MyMutations(graphene.ObjectType):
	create_notification = CreateNotification.Field()


class Query(graphene.ObjectType):
	notification = graphene.Field(Notification)


schema = graphene.Schema(query=Query, mutation=MyMutations)
