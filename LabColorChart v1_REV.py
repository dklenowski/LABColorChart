import numpy as np
import PySimpleGUI as sg
import os
import colorsys
import matplotlib.pyplot as plt
import tempfile
import atexit


def create_lab_color_chart(L_valores, a_valores, b_valores, imagem_path):
    def close_event(event):
        # Limpa os dados quando a janela de plotagem é fechada
        L_valores.clear()
        a_valores.clear()
        b_valores.clear()

    try:
        # Carrega a imagem
        imagem = plt.imread(imagem_path)

        # Cria uma figura e um eixo
        fig, ax = plt.subplots()

        # Exibe a imagem como fundo do gráfico
        ax.imshow(imagem, extent=[-100, 100, -100, 100], alpha=1)

        # Gráfico de dispersão para pontos de cor LAB
        scatter = ax.scatter(
            a_valores, b_valores,
            color=['none' if x >= 0 and y >= 0 else 'none' for x,
                   y in zip(a_valores, b_valores)],
            edgecolors='black', linewidths=1.5
        )

        # Anota pontos no gráfico
        for a, b in zip(a_valores, b_valores):
            ax.annotate(f'({a};{b})', (a, b), textcoords="offset points",
                        xytext=(0, 5), ha='center', va='bottom')

        # Adiciona rótulos e título
        ax.set_ylabel('a*')
        ax.set_xlabel('b*')
        ax.set_title('CIELab')

        # Adiciona linhas de referência para os eixos X e Y
        ax.axhline(0, color='black', linewidth=0.7, linestyle='--')
        ax.axvline(0, color='black', linewidth=0.5, linestyle='--')

        # Configurações de grade
        plt.grid(True, linestyle='--', alpha=0.6)

        # Define limites dos eixos
        ax.set_xlim(-100, 100)
        ax.set_ylim(-100, 100)

        # Adiciona uma barra de gradiente preto e branco
        cax = fig.add_axes([0.85, 0.1, 0.04, 0.79])
        cmap = plt.cm.gray
        norm = plt.Normalize(0, 100)
        cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), cax=cax)
        cb.set_label('L*')

        # Adiciona um ponto na barra de cores
        point = L_valores
        normalized_point = point
        cb.ax.plot([0, 1], [normalized_point, normalized_point],
                   color='red', linewidth=5, marker='_', markersize=8, label='Manual Point')

        # Adiciona o evento de fechamento da janela de plotagem
        fig.canvas.mpl_connect('close_event', close_event)

        # Exibe o gráfico
        plt.show()

    except Exception as e:
        sg.popup_error(f"Erro ao exibir o gráfico: {str(e)}")


def generate_color_wheel():
    num_points = 360
    hues = np.linspace(0, 1, num_points)
    saturations = np.linspace(0, 1, num_points)
    lightness = 0.5  # Luminosidade em 50%

    # Cria uma grade 2D de valores
    hsl_values = np.array([[hue, saturation, lightness]
                          for hue in hues for saturation in saturations])

    # Converte para RGB
    rgb_values = np.array([colorsys.hls_to_rgb(h, l, s)
                          for h, s, l in hsl_values])

    # Reformula os arrays para plotagem
    hues = hsl_values[:, 0].reshape((num_points, num_points))
    saturations = hsl_values[:, 1].reshape((num_points, num_points))
    rgb_values = rgb_values.reshape((num_points, num_points, 3))

    # Plota a roda de cores ajustada ao espaço de cores LAB
    fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
    ax.set_theta_direction(1)
    ax.set_theta_offset(np.pi / 6.0)
    ax.set_position([0, 0, 1, 1])  # Ajusta a posição e o tamanho
    ax.set_rlabel_position(1)

    # Adiciona escala de 0 a 100 ao longo do raio
    r_ticks = np.linspace(0, 1, 6)
    r_labels = [f'{int(t*100)}' for t in r_ticks]
    ax.set_yticks(r_ticks)
    ax.set_yticklabels(r_labels, color='gray', fontsize=8)

    c = ax.pcolormesh(hues * 2 * np.pi, saturations, rgb_values)

    # Remove rótulos e linhas de grade dos eixos
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(False)

    # Função para excluir o arquivo temporário no encerramento do programa
    def excluir_arquivo_temporario(file_path):
        os.unlink(file_path)

    # Criar um arquivo temporário
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        image_path = temp_file.name

    # Salva o gráfico gerado como um arquivo de imagem
    image_path = 'color_wheel.png'
    plt.savefig(image_path, dpi=100, bbox_inches='tight', pad_inches=0)
    plt.close()

    # Registrar a função para excluir o arquivo temporário no encerramento do programa
    atexit.register(excluir_arquivo_temporario, image_path)

    return image_path


def main():
    sg.theme('DarkGrey11')

    # Layout da GUI
    layout = [
        [sg.Text('')],  # Linha em branco
        [sg.Text('Informe os valores de L*a*b*:', size=(20, 1), justification='center')],
        [sg.Text('')],  # Linha em branco
        [sg.Text('L*:', size=(2, 1)), sg.InputText(key='L')],
        [sg.Text('a*:', size=(2, 1)), sg.InputText(key='a')],
        [sg.Text('b*:', size=(2, 1)), sg.InputText(key='b')],
        [sg.Text('')],  # Linha em branco
        [sg.Button('Mostrar', size=(10, 1)), sg.Button('Limpar', size=(10, 1)), sg.Button('Sair', size=(10, 1))],
        [sg.Text('')],  # Linha em branco
        [sg.Text('')],  # Linha em branco
        [sg.Text('2024 © LAB Color Chart v.1.2', size=(30, 1), font=('Arial Bold', 8), justification='center')]
    ]

    # Cria a janela com o ícone 
    window = sg.Window('LAB Color Chart', 
                       layout, 
                       # icon="C:/Users/arlie/OneDrive/CIELAB/TESTE/CIELAB.ico", 
                       size=(500, 300), 
                       element_justification='center')

    L_valores = []
    a_valores = []
    b_valores = []

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Sair':
            break

        if event == 'Mostrar':
            try:
                L_valores.append(float(values['L']))
                a_valores.append(float(values['a']))
                b_valores.append(float(values['b']))

                # Gera a roda de cores
                imagem_path = generate_color_wheel()

                # Exibe o gráfico de cores LAB usando a roda de cores gerada
                create_lab_color_chart(
                    L_valores, a_valores, b_valores, imagem_path)

            except ValueError:
                sg.popup_ok('Por favor, insira valores válidos para L*a*b*.')

        if event == 'Limpar':
            # Limpa os valores L*, a* e b*
            window['L'].update('')
            window['a'].update('')
            window['b'].update('')
            L_valores.clear()
            a_valores.clear()
            b_valores.clear()

    window.close()


if __name__ == "__main__":
    main()
