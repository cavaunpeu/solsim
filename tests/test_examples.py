def test_lotka_volterra():
    from examples.lotka_volterra.run import main

    main()


def test_drunken_escrow():
    from examples.drunken_escrow.run import main

    main(n_escrows=2, n_steps=2)
