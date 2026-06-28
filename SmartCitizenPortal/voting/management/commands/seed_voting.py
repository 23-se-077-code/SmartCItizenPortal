from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from voting.models import *
from datetime import date
import random

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old data...")
        Candidate.objects.all().delete()
        Constituency.objects.all().delete()
        AssemblyType.objects.all().delete()
        Province.objects.all().delete()
        Vote.objects.all().delete()
        UserProfile.objects.all().delete()

        # Build Provinces
        provinces_data = [
            ("Islamabad", "IS"), ("Punjab", "PB"), ("Sindh", "SD"),
            ("Khyber Pakhtunkhwa", "KP"), ("Balochistan", "BL"),
            ("Gilgit Baltistan", "GB"), ("Kashmir", "AJK"),
        ]
        for name, code in provinces_data:
            Province.objects.get_or_create(name=name, code=code)

        # Build Assemblies
        assemblies_config = {
            "IS": [("NA", "National Assembly")],
            "PB": [("NA", "National Assembly"), ("PP", "Punjab Assembly")],
            "SD": [("NA", "National Assembly"), ("PS", "Sindh Assembly")],
            "KP": [("NA", "National Assembly"), ("PK", "KPK Assembly")],
            "BL": [("NA", "National Assembly"), ("PB", "Balochistan Assembly")],
            "GB": [("NA", "National Assembly"), ("PG", "Gilgit Assembly")],
            "AJK": [("NA", "National Assembly"), ("PKS", "Kashmir Assembly")],
        }
        for prov_code, assems in assemblies_config.items():
            province = Province.objects.get(code=prov_code)
            for code, name in assems:
                AssemblyType.objects.get_or_create(code=code, province=province, defaults={"name": name})

        # Constituency ranges
        range_mapping = {
            "IS": {"NA": (51, 55)}, 
            "PB": {"NA": (56, 60), "PP": (11, 15)},
            "KP": {"NA": (61, 65), "PK": (16, 20)}, 
            "BL": {"NA": (66, 70), "PB": (21, 25)}, 
            "SD": {"NA": (71, 75), "PS": (26, 30)},
            "AJK": {"NA": (76, 80), "PKS": (31, 35)}, 
            "GB": {"NA": (81, 85), "PG": (36, 40)},
        }

        # Specific Candidate Profiles – align with image names
        specific_na = [
            {"name": "Syed Azadar Naqvi", "party": "Computer Science Party", "constituency": "NA-52", "photo": "candidates/azadar.jpg"},
            {"name": "Daniyal Raza Khan", "party": "Database Party", "constituency": "NA-52", "photo": "candidates/daniyal.jpg"},
            {"name": "Aseed Khan", "party": "Network Party", "constituency": "NA-53", "photo": "candidates/aseed.jpg"},
            {"name": "Malik Saifullah", "party": "AI Party", "constituency": "NA-53", "photo": "candidates/saif.jpg"},
            {"name": "Mubashir Ahmed", "party": "Cybersecurity Party", "constituency": "NA-54", "photo": "candidates/mubashir.jpg"},
            {"name": "Abdul Rafay", "party": "Software Engineering Party", "constituency": "NA-54", "photo": "candidates/rafay.jpg"},
            {"name": "Malik Hammad", "party": "Cloud Party", "constituency": "NA-55", "photo": "candidates/hammad.jpg"},
            {"name": "Aryan Butt", "party": "DevOps Party", "constituency": "NA-55", "photo": "candidates/aryan.jpg"},
            {"name": "Uzair Kiani", "party": "Independent", "constituency": "NA-56", "photo": "candidates/uzair.jpg"},
            {"name": "Mahar Hussnain Zafar", "party": "Computer Science Party", "constituency": "NA-56", "photo": "candidates/husnian.jpg"},
        ]
        specific_pa = [
            {"name": "Syed Azadar Naqvi", "party": "Computer Science Party", "constituency": "PP-11", "photo": "candidates/azadar.jpg"},
            {"name": "Daniyal Raza Khan", "party": "Database Party", "constituency": "PP-12", "photo": "candidates/daniyal.jpg"},
            {"name": "Aseed Khan", "party": "Network Party", "constituency": "PP-12", "photo": "candidates/aseed.jpg"},
            {"name": "Malik Saifullah", "party": "AI Party", "constituency": "PP-13", "photo": "candidates/saif.jpg"},
            {"name": "Mubashir Ahmed", "party": "Cybersecurity Party", "constituency": "PP-13", "photo": "candidates/mubashir.jpg"},
            {"name": "Abdul Rafay", "party": "Software Engineering Party", "constituency": "PP-14", "photo": "candidates/rafay.jpg"},
            {"name": "Malik Hammad", "party": "Cloud Party", "constituency": "PP-14", "photo": "candidates/hammad.jpg"},
            {"name": "Aryan Butt", "party": "DevOps Party", "constituency": "PP-15", "photo": "candidates/aryan.jpg"},
            {"name": "Uzair Kiani", "party": "Independent", "constituency": "PP-15", "photo": "candidates/uzair.jpg"},
            {"name": "Mahar Hussnain Zafar", "party": "Computer Science Party", "constituency": "PP-11", "photo": "candidates/husnian.jpg"},
        ]

        # Generate constituencies and candidates
        for prov_code, configs in range_mapping.items():
            province = Province.objects.get(code=prov_code)
            for ass_code, (start, end) in configs.items():
                assembly = AssemblyType.objects.get(code=ass_code, province=province)
                for num in range(start, end + 1):
                    constituency_code = f"{ass_code}-{num}"
                    constituency, _ = Constituency.objects.get_or_create(
                        code=constituency_code, assembly=assembly, province=province,
                        defaults={"name": f"{ass_code} Constituency {num}"}
                    )
                    
                    spec_list = specific_na if ass_code == 'NA' else specific_pa
                    added = 0
                    for spec in spec_list:
                        if spec['constituency'] == constituency_code:
                            Candidate.objects.get_or_create(
                                name=spec['name'], party=spec['party'], constituency=constituency,
                                defaults={'votes': 0, 'photo': spec['photo']}
                            )
                            added += 1
                            
                    if added < 3:
                        parties = ["Computer Science Party", "Database Party", "Network Party", "AI Party", "Cybersecurity Party"]
                        first_names = ["Ali", "Ahmed", "Sara", "Fatima", "Muhammad", "Zara", "Usman", "Aisha"]
                        last_names = ["Khan", "Ahmed", "Ali", "Hussain", "Bukhari", "Shah", "Malik", "Butt"]
                        for i in range(added, 3):
                            Candidate.objects.get_or_create(
                                name=f"{random.choice(first_names)} {random.choice(last_names)}",
                                party=random.choice(parties), constituency=constituency,
                                defaults={'votes': 0, 'photo': 'candidates/default.jpg'}
                            )
        
        # Test accounts setup
        user_mapping = {
            "azadar": ("NA-52", "PP-11"), "daniyal": ("NA-52", "PP-12"),
            "aseed": ("NA-53", "PP-12"), "saifullah": ("NA-53", "PP-13"),
            "mubashir": ("NA-54", "PP-13"), "rafay": ("NA-54", "PP-14"),
            "hammad": ("NA-55", "PP-14"), "aryan": ("NA-55", "PP-15"),
            "uzair": ("NA-56", "PP-15"), "hussnain": ("NA-56", "PP-11"),
        }
        for username, (na_code, pa_code) in user_mapping.items():
            user, _ = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
            user.set_password('test123')
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.date_of_birth = date(2000, 1, 1)
            profile.is_verified = True
            profile.assigned_na_constituency = Constituency.objects.get(code=na_code)
            profile.assigned_pa_constituency = Constituency.objects.get(code=pa_code)
            profile.save()
            
        self.stdout.write(self.style.SUCCESS(f"Complete alignment successful! Constituencies: {Constituency.objects.count()}, Candidates: {Candidate.objects.count()}"))