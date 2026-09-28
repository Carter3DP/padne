"""Regression tests for custom KiCad copper-layer display names."""

from types import SimpleNamespace

from padne import kicad


def test_stackup_uses_custom_copper_layer_names(tmp_path, monkeypatch):
    pcb_path = tmp_path / "custom_layers.kicad_pcb"
    pcb_path.write_text("""(kicad_pcb
        (setup (stackup
            (layer "F.Cu" (type "copper") (thickness 0.035))
            (layer "dielectric 1" (type "core") (thickness 0.31))
            (layer "In1.Cu" (type "copper") (thickness 0.035))
            (layer "dielectric 2" (type "prepreg") (thickness 0.73))
            (layer "In2.Cu" (type "copper") (thickness 0.035))
            (layer "dielectric 3" (type "core") (thickness 0.31))
            (layer "B.Cu" (type "copper") (thickness 0.035))
        ))
    )""", encoding="utf-8")

    names = {
        0: ("F.Cu", "F.Cu"),
        4: ("In1.Cu", "Inner1.Cu"),
        6: ("In2.Cu", "Inner2.Cu"),
        2: ("B.Cu", "B.Cu"),
    }

    class Board:
        def GetFileName(self):
            return str(pcb_path)

        def GetStandardLayerName(self, layer_id):
            return names[layer_id][0]

        def GetLayerName(self, layer_id):
            return names[layer_id][1]

    monkeypatch.setattr(kicad, "copper_layers", lambda board: iter(names))
    stackup = kicad.extract_stackup_from_kicad_pcb(Board())

    assert [item.name for item in stackup.items] == [
        "F.Cu", "dielectric 1", "Inner1.Cu",
        "dielectric 2", "Inner2.Cu", "dielectric 3", "B.Cu",
    ]
    plotted = [SimpleNamespace(name=name) for _, name in names.values()]
    assert kicad.verify_stackup_contains_all_layers(stackup, plotted)
    assert stackup.index_by_name("Inner1.Cu") < stackup.index_by_name("Inner2.Cu")
