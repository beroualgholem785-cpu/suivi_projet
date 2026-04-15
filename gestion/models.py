from django.db import models

class Projet(models.Model):
    nom = models.CharField(max_length=200)
    budget_total = models.FloatField()

    def __str__(self):
        return self.nom


class Situation(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    date = models.DateField()
    montant = models.FloatField()
    cumul = models.FloatField(blank=True, null=True)
    pourcentage = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # calcul du cumul
        situations = Situation.objects.filter(projet=self.projet)
        total = sum(s.montant for s in situations)

        self.cumul = total

        # calcul pourcentage
        if self.projet.budget_total > 0:
            self.pourcentage = (total / self.projet.budget_total) * 100

        super().save(update_fields=["cumul", "pourcentage"])

    def __str__(self):
        return f"{self.projet.nom} - {self.montant}"