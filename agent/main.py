from layers.page_extraction import extraer_legal_financiero_estricto


def main():
    print("Running MPC server")
    
    extraer_legal_financiero_estricto("decreto_1165_2019.pdf", pausa_debug=True)

if __name__ == "__main__":
    main()


