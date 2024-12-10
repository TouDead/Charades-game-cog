from charades.game import Charades
from charades.managment import CharadesManagement


async def setup(bot):
    await bot.add_cog(Charades(bot))
    await bot.add_cog(CharadesManagement(bot))
