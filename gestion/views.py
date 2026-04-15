from django.shortcuts import render
from django.http import HttpResponse
from .models import Projet, Situation
import pandas as pd


# 🔹 DASHBOARD (OBLIGATOIRE)
def dashboard(request):
    projets = Projet.objects.all()
    selected = request.GET.get('projet')

    projets_data = []

    for p in projets:
        if selected and str(p.id) != selected:
            continue

        situations = Situation.objects.filter(projet=p)
        cumul = sum(s.montant for s in situations)

        pourcentage = 0
        if p.budget_total > 0:
            pourcentage = (cumul / p.budget_total) * 100

        projets_data.append({
            "id": p.id,
            "nom": p.nom,
            "budget": p.budget_total,
            "cumul": cumul,
            "pourcentage": round(pourcentage, 2)
        })

    return render(request, "dashboard.html", {
        "projets": projets_data,
        "all_projets": projets
    })

# 🔹 IMPORT EXCEL
def import_excel(request):
    file_path = "C:/Users/DELL/Desktop/SUIVI_PCH_BERRAHAL_V7.xlsx"

    try:
        df = pd.read_excel(file_path, header=None)

        projet = None
        budget = 0

        for index, row in df.iterrows():
            texte = " ".join([str(x) for x in row if str(x) != "nan"])

            if not texte:
                continue

            if "Pharmacie" in texte:
                projet, _ = Projet.objects.get_or_create(
                    nom=texte,
                    budget_total=budget
                )

            if "Budget" in texte:
                try:
                    budget = float(row[1])
                except:
                    budget = 0

                if projet:
                    projet.budget_total = budget
                    projet.save()

            for cell in row:
                try:
                    montant = float(cell)

                    if montant > 1000 and projet:
                        Situation.objects.create(
                            projet=projet,
                            montant=montant,
                            date="2024-01-01"
                        )
                except:
                    pass

        return HttpResponse("✅ Import complet réussi")

    except Exception as e:
        return HttpResponse(f"❌ Erreur : {e}")

def export_pdf(request):
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from django.http import HttpResponse
    from .models import Projet, Situation

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    elements = []

    projets = Projet.objects.all()

    for p in projets:
        situations = Situation.objects.filter(projet=p)
        cumul = sum(s.montant for s in situations)

        texte = f"Projet: {p.nom} | Budget: {p.budget_total} | Cumul: {cumul}"
        elements.append(Paragraph(texte, styles['Normal']))

    doc.build(elements)

    return response