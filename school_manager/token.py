from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type


class TokenGenerator(PasswordResetTokenGenerator):
	def _make_hash_value(self,ecole,timestamp):
		return(text_type(ecole.id)+text_type(timestamp))



generator_token=TokenGenerator()