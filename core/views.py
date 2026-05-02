from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth

from .models import Movimentacao, Item
from .forms import ItemFormSet, MovimentacaoForm


# =========================
# 🏠 HOME
# =========================
@login_required
def home(request):
    dados = Movimentacao.objects.all().order_by('-data').prefetch_related('itens')

    busca = request.GET.get('busca', '').strip()
    nf = request.GET.get('nf', '').strip()
    tipo = request.GET.get('tipo', '')

    if busca:
        dados = dados.filter(
            Q(nf__icontains=busca) |
            Q(fornecedor__icontains=busca)
        )

    if nf:
        dados = dados.filter(nf__icontains=nf)

    if tipo:
        dados = dados.filter(tipo=tipo)

    agrupado = {}

    for mov in dados:
        agrupado.setdefault(mov.nf, {
            'fornecedor': mov.fornecedor,
            'data': mov.data,
            'movs': []
        })
        agrupado[mov.nf]['movs'].append(mov)

    return render(request, 'home.html', {
        'agrupado': agrupado,
        'tipos': Movimentacao.TIPOS,
        'filtros': request.GET
    })


# =========================
# 📄 GERAR PDF
# =========================
@login_required
def gerar_pdf_nf(request, nf):
    movs = Movimentacao.objects.filter(nf=nf).prefetch_related('itens')

    if not movs.exists():
        return HttpResponse("NF não encontrada")

    mov_ref = movs.first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="NF_{nf}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # =========================
    # HEADER
    # =========================
    c.setFont("Courier", 9)
    c.drawString(40, height - 40, "Prysmian Cabos Sist Br")

    c.setFont("Courier-Bold", 11)
    c.drawCentredString(width / 2, height - 55, "CONFERÊNCIA FÍSICA DE ENTRADA")

    c.setFont("Courier", 9)

    # =========================
    # DATA
    # =========================
    y = height - 80
    c.drawString(40, y, f"DATA ENTRADA: {mov_ref.data}")

    # =========================
    # CHECKBOX
    # =========================
    y -= 25
    box_size = 8

    def draw_checkbox(x, y, marcado):
        c.rect(x, y - box_size, box_size, box_size)
        if marcado:
            c.line(x, y - box_size, x + box_size, y)
            c.line(x, y, x + box_size, y - box_size)

    tipos = Movimentacao.TIPOS
    metade = (len(tipos) + 1) // 2

    for i in range(metade):
        if i < len(tipos[:metade]):
            codigo, nome = tipos[i]
            draw_checkbox(40, y, mov_ref.tipo == codigo)
            c.drawString(55, y - 6, nome.upper())

        if i < len(tipos[metade:]):
            codigo, nome = tipos[i + metade]
            draw_checkbox(300, y, mov_ref.tipo == codigo)
            c.drawString(315, y - 6, nome.upper())

        y -= 14

    # =========================
    # BLOCO NF
    # =========================
    y -= 10
    c.drawString(40, y, f"DOCUMENTO/ANO: {nf}")

    y -= 14
    c.drawString(40, y, f"SÉRIE/NUM.NF: {nf}")
    c.drawString(300, y, f"DATA NF: {mov_ref.data}")

    y -= 14
    c.drawString(40, y, f"FORNECEDOR: {mov_ref.fornecedor}")

    # =========================
    # FUNÇÃO CENTRALIZAR
    # =========================
    def draw_centered(text, x1, x2, y):
        text = str(text or "")
        largura = stringWidth(text, "Courier", 9)
        c.drawString((x1 + x2) / 2 - largura / 2, y, text)

    # =========================
    # TABELA
    # =========================
    y -= 30

    x_cols = [40, 85, 160, 380, 430, 500]
    headers = ["ITEM", "MATERIAL", "DESCRIÇÃO", "UN", "QTD", "DIV"]

    row_height = 14
    num_rows = 12

    table_top = y
    table_bottom = table_top - (row_height * (num_rows + 1))

    c.rect(40, table_bottom, 510, (table_top - 15) - table_bottom)

    c.setFont("Courier-Bold", 9)
    for i, h in enumerate(headers):
        x2 = x_cols[i + 1] if i + 1 < len(x_cols) else 550
        draw_centered(h, x_cols[i], x2, table_top - 12)

    c.line(40, table_top - 15, 550, table_top - 15)

    for i in range(num_rows + 1):
        y_line = table_top - 15 - (i * row_height)
        c.line(40, y_line, 550, y_line)

    for x in x_cols[1:]:
        c.line(x, table_top - 15, x, table_bottom)

    # =========================
    # DADOS
    # =========================
    c.setFont("Courier", 9)

    linha_y = table_top - 15 - row_height + 3
    linha = 0

    for mov in movs:
        for item in mov.itens.all().order_by('numero'):

            if linha >= num_rows:
                break

            draw_centered(str(item.numero).zfill(5), x_cols[0], x_cols[1], linha_y)
            c.drawString(x_cols[1] + 2, linha_y, (item.material or "")[:15])
            c.drawString(x_cols[2] + 2, linha_y, (item.descricao or "")[:40])

            draw_centered(item.unidade, x_cols[3], x_cols[4], linha_y)
            draw_centered(item.quantidade, x_cols[4], x_cols[5], linha_y)
            draw_centered(item.div, x_cols[5], 550, linha_y)

            linha_y -= row_height
            linha += 1

        if linha >= num_rows:
            break

    # =========================
    # RODAPÉ
    # =========================
    y = table_bottom - 30

    c.drawString(40, y, f"LOCAL DE ENTREGA: {mov_ref.get_local_display()}")

    y -= 18
    c.drawString(40, y, f"PLACA DO VEÍCULO: {mov_ref.placa}")

    y -= 18
    c.drawString(40, y, f"OBS: {(mov_ref.obs or '')[:100]}")

    # =========================
    # ASSINATURAS
    # =========================
    y -= 40

    def draw_assinatura(x, titulo, cartao):
        c.drawCentredString(x, y, "_" * 25)
        c.drawCentredString(x, y - 12, titulo)
        c.drawCentredString(x, y - 28, f"Cartão:....... {cartao or ''}")

    if mov_ref.visto_conferente and mov_ref.visto_patio:
        draw_assinatura(width / 4, "VISTO DO PÁTIO", mov_ref.cartao_patio)
        draw_assinatura((width / 4) * 3, "VISTO DO CONFERENTE", mov_ref.cartao_conferente)

    elif mov_ref.visto_conferente:
        draw_assinatura(width / 2, "VISTO DO CONFERENTE", mov_ref.cartao_conferente)

    elif mov_ref.visto_patio:
        draw_assinatura(width / 2, "VISTO DO PÁTIO", mov_ref.cartao_patio)

    else:
        c.drawCentredString(width / 2, y, "_" * 25)

    c.save()
    return response


# =========================
# ➕ NOVA MOVIMENTAÇÃO
# =========================
@login_required
def nova_movimentacao(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)
        formset = ItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():

            mov = form.save()
            itens = formset.save(commit=False)

            numero = 1
            for item in itens:
                if not item.material:
                    continue

                item.movimentacao = mov
                item.numero = numero
                item.save()
                numero += 1

            for obj in formset.deleted_objects:
                obj.delete()

            return redirect('home')

        else:
            print("❌ FORM:", form.errors)
            print("❌ FORMSET:", formset.errors)

    else:
        form = MovimentacaoForm()
        formset = ItemFormSet()

    return render(request, 'form_completo.html', {
        'form': form,
        'formset': formset
    })


# =========================
# ✏️ EDITAR
# =========================
@login_required
def editar_movimentacao(request, id):
    mov = get_object_or_404(Movimentacao, id=id)

    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, instance=mov)
        formset = ItemFormSet(request.POST, instance=mov)

        # ✅ CORREÇÃO PRINCIPAL
        if form.is_valid() and formset.is_valid():

            mov = form.save()

            # salva sem commit
            itens = formset.save(commit=False)

            # pega último número existente
            ultimo_numero = mov.itens.aggregate(
                Max('numero')
            )['numero__max'] or 0

            for item in itens:

                # ignora item vazio
                if not item.material:
                    continue

                item.movimentacao = mov

                # só define número se for novo
                if not item.id:
                    ultimo_numero += 1
                    item.numero = ultimo_numero

                item.save()

            # 🔥 ESSENCIAL
            for obj in formset.deleted_objects:
                obj.delete()

            return redirect('home')

        else:
            print("❌ FORM ERRO:", form.errors)
            print("❌ FORMSET ERRO:", formset.errors)

    else:
        form = MovimentacaoForm(instance=mov)
        formset = ItemFormSet(instance=mov)

    return render(request, 'form_completo.html', {
        'form': form,
        'formset': formset,
        'mov': mov
    })

# =========================
# 🗑️ EXCLUIR
# =========================
@login_required
def excluir_nf(request, nf):
    movs = Movimentacao.objects.filter(nf=nf)

    if request.method == 'POST':
        movs.delete()
        return redirect('home')

    return render(request, 'confirmar_exclusao.html', {'nf': nf})


@login_required
def excluir_item(request, id):
    item = get_object_or_404(Item, id=id)
    mov = item.movimentacao

    item.delete()

    itens = mov.itens.all().order_by('numero')
    for i, item in enumerate(itens, start=1):
        item.numero = i
        item.save()

    return redirect('home')