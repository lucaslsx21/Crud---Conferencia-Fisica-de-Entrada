from django.db import models


# =========================
# 📦 MOVIMENTAÇÃO
# =========================
class Movimentacao(models.Model):

    TIPOS = [
        ("TRANSFERENCIA", "Transferência entre fábricas"),
        ("EMPRESTIMO", "Empréstimo Terceiros (MP)"),
        ("MATERIAIS", "Materiais recebido como amostras"),
        ("RECEBIDO", "Material recebido p/ transformação"),
        ("DEMONSTRACAO", "Material recebido como demonstração"),
        ("ENTRADA", "Entrada de acondicionamento"),
        ("REMESSA", "Remessa merc. fatur. antecipado"),
        ("FABRICAS", "Retorno empréstimos env. à terceiros"),
        ("DEVOLVER", "Devoluções"),
        ("CONSERTO", "Retorno de conserto"),
        ("TESTE", "Material recebido para teste"),
        ("ACONDICIONAR", "Retorno acondicionamento"),
        ("TRANSFORMAR", "Retorno de material não transformado"),
        ("OUTROS", "Outros:..................."),
    ]

    LOCAIS = [
        ("VILA_VELHA", "Vila Velha"),
        ("CARIACICA", "Cariacica"),
    ]

    data = models.DateField()
    tipo = models.CharField(max_length=50, choices=TIPOS)

    fornecedor = models.CharField(max_length=200)
    nf = models.CharField(max_length=50)
    cfop = models.CharField(max_length=20, blank=True, null=True)
    div = models.CharField(max_length=20, blank=True)

    local = models.CharField(max_length=50, choices=LOCAIS)
    placa = models.CharField(max_length=20)

    obs = models.TextField(blank=True)

    visto_patio = models.BooleanField(default=False)
    visto_conferente = models.BooleanField(default=False)

    cartao_patio = models.CharField(max_length=50, blank=True)
    cartao_conferente = models.CharField(max_length=50, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nf} - {self.fornecedor}"


# =========================
# 📋 ITEM
# =========================
class Item(models.Model):

    movimentacao = models.ForeignKey(
        Movimentacao,
        on_delete=models.CASCADE,
        related_name='itens'
    )

    numero = models.IntegerField()

    material = models.CharField(max_length=100)
    unidade = models.CharField(max_length=20)
    div = models.CharField(max_length=20, blank=True)

    descricao = models.TextField()
    quantidade = models.IntegerField()

    def __str__(self):
        return f"Item {self.numero}: {self.material} ({self.quantidade})"

    class Meta:
        ordering = ['numero']