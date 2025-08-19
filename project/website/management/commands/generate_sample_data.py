# website/management/commands/generate_sample_data.py
import random
import uuid
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from website.models import Patient, PreSurgeryForm, PostDuringSurgeryForm
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate sample data for testing ALPHA Project'

    def add_arguments(self, parser):
        parser.add_argument(
            '--patients',
            type=int,
            default=50,
            help='Number of patients to create (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before creating new'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing sample data...')
            # Only delete patients created by sample data (with specific pattern)
            Patient.objects.filter(folio_hospitalizacion__startswith='SAMPLE-').delete()
            PreSurgeryForm.objects.filter(folio_hospitalizacion__startswith='PRE-SAMPLE-').delete()
            
        num_patients = options['patients']
        self.stdout.write(f'Creating {num_patients} sample patients...')
        
        # Get or create a sample doctor
        doctor = self.get_or_create_sample_doctor()
        
        for i in range(num_patients):
            try:
                patient = self.create_sample_patient(doctor, i)
                presurgery = self.create_sample_presurgery(patient)
                
                # Create post-surgery form for 80% of patients
                if random.random() < 0.8:
                    self.create_sample_postsurgery(presurgery)
                
                if (i + 1) % 10 == 0:
                    self.stdout.write(f'Created {i + 1} patients...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating patient {i + 1}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {num_patients} sample patients!')
        )

    def get_or_create_sample_doctor(self):
        """Get or create a sample doctor for testing"""
        try:
            doctor = User.objects.get(username='sample_doctor')
        except User.DoesNotExist:
            doctor = User.objects.create_user(
                username='sample_doctor',
                email='sample@alpha-project.com',
                password='samplepass123',
                nombre='Dr. Sample',
                apellidos='Anestesiólogo',
                telefono='+52 555 123 4567',
                especialidad='ANE',
                is_active=True
            )
            self.stdout.write('Created sample doctor account')
        return doctor

    def create_sample_patient(self, doctor, index):
        """Create a sample patient"""
        # Sample names
        nombres = [
            'Juan Carlos', 'María Elena', 'José Luis', 'Ana Sofía', 'Miguel Ángel',
            'Carmen Rosa', 'Ricardo', 'Patricia', 'Fernando', 'Gabriela',
            'Alberto', 'Claudia', 'Roberto', 'Mónica', 'Eduardo',
            'Alejandra', 'Francisco', 'Beatriz', 'Sergio', 'Verónica'
        ]
        
        apellidos = [
            'García López', 'Rodríguez Martín', 'González Pérez', 'Fernández Silva',
            'López Hernández', 'Martínez Torres', 'Sánchez Ruiz', 'Pérez Morales',
            'Gómez Castro', 'Martín Ortega', 'Jiménez Ramos', 'Ruiz Delgado',
            'Hernández Vega', 'Díaz Romero', 'Moreno Iglesias', 'Álvarez Núñez',
            'Romero Garrido', 'Alonso Guerrero', 'Gutiérrez Cano', 'Navarro León'
        ]
        
        # Generate realistic patient data
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        
        # Birth date (20-80 years old)
        birth_year = datetime.now().year - random.randint(20, 80)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        fecha_nacimiento = datetime(birth_year, birth_month, birth_day).date()
        
        # Create a simple barcode image
        barcode_image = self.create_sample_barcode()
        
        patient = Patient.objects.create(
            folio_hospitalizacion=f'SAMPLE-{index+1:03d}',
            nombres=nombre,
            apellidos=apellido,
            fecha_nacimiento=fecha_nacimiento,
            medico=doctor,
            codigo_barras=barcode_image
        )
        
        return patient

    def create_sample_barcode(self):
        """Create a simple sample barcode image"""
        # Create a simple black and white barcode-like image
        img = Image.new('RGB', (200, 50), color='white')
        pixels = img.load()
        
        # Create vertical lines to simulate barcode
        for x in range(0, 200, 4):
            width = random.choice([1, 2, 3])
            for y in range(50):
                for w in range(width):
                    if x + w < 200:
                        pixels[x + w, y] = (0, 0, 0)
        
        # Save to bytes
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        return SimpleUploadedFile(
            name=f'barcode_{uuid.uuid4().hex[:8]}.png',
            content=img_io.getvalue(),
            content_type='image/png'
        )

    def create_sample_presurgery(self, patient):
        """Create a sample pre-surgery form"""
        # Calculate age
        today = datetime.now().date()
        age = today.year - patient.fecha_nacimiento.year
        
        # Generate realistic medical data based on age and risk factors
        peso = random.uniform(50, 120)  # kg
        talla = random.uniform(150, 190)  # cm
        imc = peso / ((talla/100) ** 2)
        
        # ASA based on age and other factors
        if age < 30:
            asa = random.choices([1, 2, 3], weights=[60, 35, 5])[0]
        elif age < 60:
            asa = random.choices([1, 2, 3, 4], weights=[20, 50, 25, 5])[0]
        else:
            asa = random.choices([2, 3, 4, 5], weights=[30, 40, 25, 5])[0]
        
        # Mallampati based on BMI and age
        if imc > 30:
            mallampati = random.choices([1, 2, 3, 4], weights=[10, 30, 40, 20])[0]
        else:
            mallampati = random.choices([1, 2, 3, 4], weights=[40, 35, 20, 5])[0]
        
        # Generate other realistic values
        fc = random.randint(60, 100)
        ta_systolic = random.randint(110, 160)
        ta_diastolic = random.randint(70, 100)
        ta = f"{ta_systolic}/{ta_diastolic}"
        
        spo2_aire = random.randint(94, 99)
        spo2_oxigeno = random.randint(97, 100)
        glasgow = random.choices([15, 14, 13], weights=[85, 10, 5])[0]
        
        # Airway assessment
        patil_aldrete = random.choices([1, 2, 3, 4], weights=[40, 35, 20, 5])[0]
        distancia_inter_incisiva = random.uniform(2.5, 5.5)
        distancia_tiro_mentoniana = random.uniform(5.0, 8.0)
        protrusion_mandibular = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
        
        # Risk scores
        macocha = random.randint(0, 12)
        stop_bang = random.randint(0, 8)
        desviacion_traquea = random.uniform(0, 2.0)
        
        # Medical history based on age
        comorbilidades_list = []
        if age > 50:
            if random.random() < 0.3:
                comorbilidades_list.append("Hipertensión arterial")
            if random.random() < 0.2:
                comorbilidades_list.append("Diabetes mellitus tipo 2")
            if random.random() < 0.15:
                comorbilidades_list.append("Enfermedad coronaria")
        
        if imc > 30:
            comorbilidades_list.append("Obesidad")
        
        comorbilidades = ", ".join(comorbilidades_list) if comorbilidades_list else "Ninguna"
        
        # Medications
        medicamentos_list = []
        if "Hipertensión" in comorbilidades:
            medicamentos_list.append("Losartán 50mg c/24h")
        if "Diabetes" in comorbilidades:
            medicamentos_list.append("Metformina 850mg c/12h")
        
        medicamentos = ", ".join(medicamentos_list) if medicamentos_list else "Ninguno"
        
        # Allergies
        alergias_options = ["AINE", "Penicilina", "Latex", "Ninguna conocida"]
        alergias = random.choice(alergias_options)
        
        # Surgery details
        diagnosticos = [
            "Colecistitis crónica litiásica",
            "Hernia inguinal derecha",
            "Apendicitis aguda",
            "Colelitiasis sintomática",
            "Hernia umbilical",
            "Masa abdominal por estudiar",
            "Obstrucción intestinal",
            "Tumor de colon",
            "Hernia ventral",
            "Patología benigna de tiroides"
        ]
        
        presurgery = PreSurgeryForm.objects.create(
            folio_hospitalizacion=f'PRE-{patient.folio_hospitalizacion}',
            nombres=patient.nombres,
            apellidos=patient.apellidos,
            fecha_nacimiento=patient.fecha_nacimiento,
            medico=patient.medico.get_full_name(),
            fecha_reporte=datetime.now().date() - timedelta(days=random.randint(0, 30)),
            medico_tratante=patient.medico.get_full_name(),
            diagnostico_preoperatorio=random.choice(diagnosticos),
            
            # Physical measurements
            peso=round(peso, 1),
            talla=round(talla, 1),
            imc=round(imc, 2),
            estado_fisico_asa=asa,
            
            # Medical history
            comorbilidades=comorbilidades,
            medicamentos=medicamentos,
            alergias=alergias,
            ayuno_hrs=random.randint(8, 16),
            uso_glp1=random.random() < 0.1,  # 10% use GLP1
            dosis_glp1="1mg semanal" if random.random() < 0.1 else "",
            tabaquismo=random.random() < 0.2,  # 20% smokers
            
            # Difficulty history
            antecedentes_dificultad=random.random() < 0.1,  # 10% have previous difficulty
            descripcion_dificultad="Intubación difícil previa, requirió videolaringoscopio" if random.random() < 0.1 else "",
            
            # Evaluation
            evaluacion_preoperatoria=f"Paciente de {age} años, ASA {asa}, programado para cirugía electiva. Evaluación completa realizada.",
            
            # USG
            uso_usg_gastrico=random.random() < 0.3,  # 30% use USG
            usg_gastrico_ml=random.randint(50, 200) if random.random() < 0.3 else None,
            
            # Vital signs
            fc=fc,
            ta=ta,
            spo2_aire=spo2_aire,
            spo2_oxigeno=spo2_oxigeno,
            glasgow=glasgow,
            
            # Airway assessment
            mallampati=mallampati,
            patil_aldrete=patil_aldrete,
            distancia_inter_incisiva=round(distancia_inter_incisiva, 1),
            distancia_tiro_mentoniana=round(distancia_tiro_mentoniana, 1),
            protrusion_mandibular=protrusion_mandibular,
            
            # Risk scores
            macocha=macocha,
            stop_bang=stop_bang,
            desviacion_traquea=round(desviacion_traquea, 1),
            problemas_deglucion=random.random() < 0.05,  # 5%
            estridor_laringeo=random.random() < 0.02,  # 2%
            observaciones="Paciente evaluado completamente, apto para cirugía programada."
        )
        
        return presurgery

    def create_sample_postsurgery(self, presurgery):
        """Create a sample post-surgery form"""
        # Get patient for context
        patient_folio = presurgery.folio_hospitalizacion.replace('PRE-', '')
        
        # Determine difficulty based on pre-surgery risk factors
        is_difficult = (
            presurgery.mallampati >= 3 or 
            presurgery.estado_fisico_asa >= 4 or 
            presurgery.imc >= 35 or
            presurgery.antecedentes_dificultad
        )
        
        # Locations
        lugares = [
            "Quirófano 1", "Quirófano 2", "Quirófano 3",
            "Urgencias", "Sala de Procedimientos", "UCI"
        ]
        
        # Techniques based on difficulty
        if is_difficult:
            tecnicas = [
                "Videolaringoscopía", "Intubación con fibrobroncoscopio",
                "Intubación retrógrada", "Máscara laríngea como rescate"
            ]
        else:
            tecnicas = [
                "Laringoscopía directa", "Videolaringoscopía",
                "Intubación orotraqueal estándar"
            ]
        
        # Number of attempts based on difficulty
        if is_difficult:
            numero_intentos = random.choices([1, 2, 3, 4], weights=[40, 35, 20, 5])[0]
        else:
            numero_intentos = random.choices([1, 2, 3], weights=[80, 15, 5])[0]
        
        # Cormack based on Mallampati and difficulty
        if presurgery.mallampati >= 3:
            cormack = random.choices([1, 2, 3, 4], weights=[10, 30, 40, 20])[0]
        else:
            cormack = random.choices([1, 2, 3, 4], weights=[50, 35, 12, 3])[0]
        
        # POGO based on Cormack
        if cormack == 1:
            pogo = random.randint(80, 100)
        elif cormack == 2:
            pogo = random.randint(50, 79)
        elif cormack == 3:
            pogo = random.randint(20, 49)
        else:
            pogo = random.randint(0, 19)
        
        # HAN classification based on difficulty
        if numero_intentos == 1 and cormack <= 2:
            han = 0  # No difficulty
        elif numero_intentos <= 2 and cormack <= 3:
            han = 1  # Slight difficulty
        elif numero_intentos <= 3 or cormack == 4:
            han = 2  # Moderate difficulty
        else:
            han = random.choice([3, 4])  # Severe difficulty
        
        # Complications based on difficulty and attempts
        has_complications = (numero_intentos > 2 or han >= 3 or random.random() < 0.05)
        
        complicaciones_list = []
        if has_complications:
            possible_complications = [
                "Hipoxemia transitoria",
                "Bradicardia durante la inducción",
                "Hipotensión post-inducción",
                "Lesión dental menor",
                "Laringoespasmo",
                "Broncoespasmo"
            ]
            complicaciones_list = random.sample(possible_complications, random.randint(1, 2))
        
        # Anesthesia types
        tipos_anestesia = [
            "Anestesia general balanceada",
            "Anestesia general endovenosa",
            "Anestesia general inhalatoria",
            "Anestesia combinada"
        ]
        
        # Results based on complications
        if has_complications:
            resultados = [
                "Intubación exitosa con complicaciones menores",
                "Procedimiento completado satisfactoriamente con incidencias",
                "Manejo exitoso de vía aérea con dificultades"
            ]
        else:
            resultados = [
                "Procedimiento sin complicaciones",
                "Intubación exitosa al primer intento",
                "Manejo de vía aérea sin incidencias"
            ]
        
        # Specialty mapping
        especialidades_map = {
            'ANE': 'anestesiologia',
            'ANP': 'anestesiologia_pediatrica',
            'MEC': 'medicina_critica',
            'MED': 'medicina_del_dolor',
            'OTR': 'otra'
        }
        
        # Get doctor's specialty or default
        doctor_specialty = getattr(presurgery.medico, 'especialidad', 'ANE')
        especialidad = especialidades_map.get(doctor_specialty, 'anestesiologia')
        
        postsurgery = PostDuringSurgeryForm.objects.create(
            folio_hospitalizacion=presurgery,
            
            # Location and personnel
            lugar_problema=random.choice(lugares),
            presencia_anestesiologo=True,
            
            # Equipment and techniques
            tecnica_utilizada=random.choice(tecnicas),
            carro_via_aerea=random.random() < 0.8,  # 80% have difficult airway cart
            tipo_video_laringoscopia="C-MAC" if "Video" in random.choice(tecnicas) else "",
            
            # Classifications
            clasificacion_han=han,
            aditamento_via_aerea=random.choice([
                "Guía de Eschmann", "Estilete", "Ninguno", "Bougie"
            ]),
            tiempo_preoxigenacion=random.randint(3, 8),
            
            # Supraglottic device
            uso_supraglotico=random.random() < 0.2,  # 20% use supraglottic
            tipo_supraglotico="LMA Supreme #4" if random.random() < 0.2 else "",
            problemas_supragloticos="Fuga aérea mínima" if random.random() < 0.1 else "",
            
            # Intubation details
            tipo_intubacion=random.choice([
                "Orotraqueal", "Nasotraqueal", "Traqueostomía"
            ]),
            numero_intentos=numero_intentos,
            laringoscopia_directa=f"Cormack {cormack}, visualización {'buena' if cormack <= 2 else 'limitada'}",
            cormack=cormack,
            pogo=pogo,
            
            # Additional procedures
            intubacion_tecnica_mixta="Videolaringoscopía + guía" if numero_intentos > 1 else "",
            intubacion_despierto=random.random() < 0.05,  # 5% awake intubation
            descripcion_intubacion_despierto="Sedación consciente con propofol y fentanilo" if random.random() < 0.05 else "",
            
            # Anesthesia details
            tipo_anestesia=random.choice(tipos_anestesia),
            sedacion=random.choice([
                "Propofol + Fentanilo", "Midazolam + Fentanilo", "Dexmedetomidina"
            ]),
            cooperacion_paciente=random.choice([
                "Excelente", "Buena", "Regular", "Limitada"
            ]),
            
            # Emergency procedures
            algoritmo_no_intubacion=numero_intentos >= 4,
            crico_tiroidotomia=random.random() < 0.01,  # 1% need cricothyrotomy
            traqueostomia_percutanea=random.random() < 0.02,  # 2% need tracheostomy
            
            # Outcomes
            complicaciones=", ".join(complicaciones_list) if complicaciones_list else "",
            resultado_final=random.choice(resultados),
            
            # Morbidity and mortality
            morbilidad=has_complications and random.random() < 0.3,
            descripcion_morbilidad="Hipoxemia transitoria sin secuelas" if has_complications and random.random() < 0.3 else "",
            mortalidad=False,  # No mortality in sample data
            descripcion_mortalidad="",
            
            # Medical personnel
            nombre_anestesiologo=presurgery.medico,
            cedula_profesional=f"{random.randint(1000000, 9999999)}",
            especialidad=especialidad,
            nombre_residente=f"Dr. Residente {random.randint(1, 20)}" if random.random() < 0.4 else ""
        )
        
        return postsurgery