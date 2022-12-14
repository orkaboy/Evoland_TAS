from engine.seq import SeqList


class Aogai1(SeqList):
    def __init__(self):
        super().__init__(
            name="Aogai Village",
            children=[
                # TODO: Have a long conversation with Sid
                # TODO: Get the text glitch from card player in Aogai
                # TODO: Get bombs by talking to everyone
            ],
        )


class Aogai2(SeqList):
    def __init__(self):
        super().__init__(
            name="Aogai Village",
            children=[
                # TODO: Get heal bug (card player, healer) Exit north
            ],
        )
