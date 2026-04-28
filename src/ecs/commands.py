# Patrón Command (simplificado): cada acción es un objeto con execute(ctx).


class CommandContext:
    """Acumula intención de movimiento y disparo para un frame."""

    def __init__(self):
        self.dir_x = 0
        self.dir_y = 0
        self.fire_mx = None
        self.fire_my = None


class Command:
    def execute(self, ctx):
        raise NotImplementedError


class PlayerLeftCommand(Command):
    def execute(self, ctx):
        ctx.dir_x -= 1


class PlayerRightCommand(Command):
    def execute(self, ctx):
        ctx.dir_x += 1


class PlayerUpCommand(Command):
    def execute(self, ctx):
        ctx.dir_y -= 1


class PlayerDownCommand(Command):
    def execute(self, ctx):
        ctx.dir_y += 1


class PlayerFireCommand(Command):
    def __init__(self, mouse_x, mouse_y):
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y

    def execute(self, ctx):
        ctx.fire_mx = self.mouse_x
        ctx.fire_my = self.mouse_y
