import lightbulb
import hikari

class err_aware:
    @staticmethod
    def insufficient_perms(exception:lightbulb.MissingRequiredPermission):
        embed = hikari.Embed(
            title="Insufficient Permissions",
            description=f"You are missing permissions {exception.missing_perms}",
            color=0xFF0000,
        )
        return embed