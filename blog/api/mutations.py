import strawberry
import strawberry_django_jwt.mutations as jwt_mutations


@strawberry.type
class AuthMutation:
    token_auth = jwt_mutations.ObtainJSONWebToken.obtain
    verify_token = jwt_mutations.Verify.verify
    refresh_token = jwt_mutations.Refresh.refresh
    delete_token_cookie = jwt_mutations.DeleteJSONWebTokenCookie.delete_cookie


class PrintMutation:
    @strawberry.mutation
    def print_msg(self, msg: str) -> None:
        print(msg)
        return None


@strawberry.type
class Mutation(AuthMutation):
    print_msg = PrintMutation.print_msg
