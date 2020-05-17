from iobes.convert import (
    iob_to_bio,
    iob_to_iobes,
    iob_to_bilou,
    iob_to_bmeow,
    bio_to_iob,
    bio_to_iobes,
    bio_to_bilou,
    bio_to_bmeow,
    iobes_to_iob,
    iobes_to_bio,
    iobes_to_bilou,
    iobes_to_bmeow,
    bilou_to_iob,
    bilou_to_bio,
    bilou_to_iobes,
    bilou_to_bmeow,
    bmeow_to_iob,
    bmeow_to_bio,
    bmeow_to_iobes,
    bmeow_to_bilou,
)
from utils import generate_spans, generate_iobes, generate_bilou, generate_bmeow, generate_iob, generate_bio


TRIALS = 100
PAIRS = (
    ((iob_to_bio, bio_to_iob), (generate_iob, generate_bio)),
    ((iob_to_iobes, iobes_to_iob), (generate_iob, generate_iobes)),
    ((iob_to_bilou, bilou_to_iob), (generate_iob, generate_bilou)),
    ((iob_to_bmeow, bmeow_to_iob), (generate_iob, generate_bmeow)),
    ((bio_to_iobes, iobes_to_bio), (generate_bio, generate_iobes)),
    ((bio_to_bilou, bilou_to_bio), (generate_bio, generate_bilou)),
    ((bio_to_bmeow, bmeow_to_bio), (generate_bio, generate_bmeow)),
    ((iobes_to_bilou, bilou_to_iobes), (generate_iobes, generate_bilou)),
    ((iobes_to_bmeow, bmeow_to_iobes), (generate_iobes, generate_bmeow)),
    ((bilou_to_bmeow, bmeow_to_bilou), (generate_bilou, generate_bmeow)),
)


def test_conversions():
    def test():
        for ((c1, c2), (g1, g2)) in PAIRS:
            spans, length = generate_spans(["A", "B", "C", "D"])
            src = g1(spans, length)
            tgt = g2(spans, length)

            assert c1(src) == tgt
            assert c2(tgt) == src
            assert c2(c1(src)) == src
            assert c1(c2(tgt)) == tgt

    for _ in range(TRIALS):
        test()
