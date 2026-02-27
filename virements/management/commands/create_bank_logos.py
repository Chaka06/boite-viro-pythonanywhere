from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import os

class Command(BaseCommand):
    help = 'Créer des logos professionnels pour toutes les banques'

    def handle(self, *args, **options):
        # Créer le dossier des logos
        logos_dir = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'virements', 'images', 'logos')
        os.makedirs(logos_dir, exist_ok=True)
        
        # Définition des banques avec leurs couleurs et styles
        banques = {
            'bnp_paribas': {
                'name': 'BNP PARIBAS',
                'short': 'BNP',
                'color': (0, 150, 82),
                'text_color': 'white',
                'style': 'modern'
            },
            'credit_agricole': {
                'name': 'CRÉDIT AGRICOLE', 
                'short': 'CA',
                'color': (0, 150, 130),
                'text_color': 'white',
                'style': 'classic'
            },
            'bnp_paribas_fortis': {
                'name': 'BNP PARIBAS FORTIS',
                'short': 'BPF',
                'color': (0, 100, 180),
                'text_color': 'white',
                'style': 'elegant'
            },
            'credit_mutuel': {
                'name': 'CRÉDIT MUTUEL',
                'short': 'CM',
                'color': (0, 80, 150),
                'text_color': 'white',
                'style': 'modern'
            },
            'credit_suisse': {
                'name': 'CREDIT SUISSE',
                'short': 'CS',
                'color': (200, 16, 46),
                'text_color': 'white',
                'style': 'premium'
            },
            'credit_lyonnais': {
                'name': 'CRÉDIT LYONNAIS',
                'short': 'CL',
                'color': (0, 60, 120),
                'text_color': 'white',
                'style': 'classic'
            },
            'banque_populaire': {
                'name': 'BANQUE POPULAIRE',
                'short': 'BP',
                'color': (200, 50, 50),
                'text_color': 'white',
                'style': 'modern'
            },
            'societe_generale': {
                'name': 'SOCIÉTÉ GÉNÉRALE',
                'short': 'SG',
                'color': (200, 0, 50),
                'text_color': 'white',
                'style': 'premium'
            },
            'intesa_sanpaolo': {
                'name': 'INTESA SANPAOLO',
                'short': 'ISP',
                'color': (0, 80, 150),
                'text_color': 'white',
                'style': 'elegant'
            },
            'deutsche_bank': {
                'name': 'DEUTSCHE BANK',
                'short': 'DB',
                'color': (0, 25, 80),
                'text_color': 'white',
                'style': 'premium'
            }
        }
        
        for bank_code, bank_info in banques.items():
            logo_path = os.path.join(logos_dir, f'{bank_code}.png')
            self.create_professional_logo(logo_path, bank_info)
            self.stdout.write(
                self.style.SUCCESS(f'Logo créé pour {bank_info["name"]} : {logo_path}')
            )
    
    def create_professional_logo(self, logo_path, bank_info):
        """Créer un logo professionnel pour une banque"""
        # Dimensions du logo
        width, height = 300, 200
        
        # Créer l'image de base
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Couleurs
        primary_color = bank_info['color']
        text_color = bank_info['text_color']
        
        if bank_info['style'] == 'modern':
            self.draw_modern_style(draw, width, height, primary_color, bank_info['short'], text_color)
        elif bank_info['style'] == 'classic':
            self.draw_classic_style(draw, width, height, primary_color, bank_info['short'], text_color)
        elif bank_info['style'] == 'elegant':
            self.draw_elegant_style(draw, width, height, primary_color, bank_info['short'], text_color)
        elif bank_info['style'] == 'premium':
            self.draw_premium_style(draw, width, height, primary_color, bank_info['short'], text_color)
        
        # Sauvegarder le logo
        img.save(logo_path, 'PNG', quality=95, optimize=True)
    
    def draw_modern_style(self, draw, width, height, color, text, text_color):
        """Style moderne avec formes géométriques"""
        # Fond dégradé simulé avec rectangles
        for i in range(height):
            alpha = i / height
            shade = tuple(int(c * (0.7 + 0.3 * alpha)) for c in color)
            draw.line([(0, i), (width, i)], fill=shade)
        
        # Forme géométrique moderne
        points = [(50, 100), (150, 50), (250, 100), (200, 150), (100, 150)]
        draw.polygon(points, fill='white', outline=color, width=3)
        
        # Texte centré
        self.draw_centered_text(draw, text, width//2, height//2, 36, color)
    
    def draw_classic_style(self, draw, width, height, color, text, text_color):
        """Style classique avec bordures et empattements"""
        # Fond uni
        draw.rectangle([(0, 0), (width, height)], fill=color)
        
        # Bordure décorative
        draw.rectangle([(20, 20), (width-20, height-20)], outline='white', width=4)
        draw.rectangle([(30, 30), (width-30, height-30)], outline='white', width=2)
        
        # Cercle central
        center_x, center_y = width//2, height//2
        radius = 60
        draw.ellipse([(center_x-radius, center_y-radius), 
                     (center_x+radius, center_y+radius)], 
                     fill='white', outline=color, width=3)
        
        # Texte dans le cercle
        self.draw_centered_text(draw, text, center_x, center_y, 24, color)
    
    def draw_elegant_style(self, draw, width, height, color, text, text_color):
        """Style élégant avec courbes douces"""
        # Fond avec dégradé diagonal
        for i in range(width):
            for j in range(height):
                alpha = (i + j) / (width + height)
                shade = tuple(int(c * (0.6 + 0.4 * alpha)) for c in color)
                draw.point((i, j), fill=shade)
        
        # Forme elliptique élégante
        draw.ellipse([(40, 40), (width-40, height-40)], 
                    fill=(255, 255, 255, 200), outline=color, width=4)
        
        # Lignes décoratives
        draw.arc([(60, 60), (width-60, height-60)], 0, 180, fill=color, width=2)
        draw.arc([(60, 60), (width-60, height-60)], 180, 360, fill=color, width=2)
        
        # Texte central
        self.draw_centered_text(draw, text, width//2, height//2, 32, color)
    
    def draw_premium_style(self, draw, width, height, color, text, text_color):
        """Style premium avec effets métalliques"""
        # Fond sombre
        draw.rectangle([(0, 0), (width, height)], fill=color)
        
        # Effet métallique avec lignes
        for i in range(0, width, 10):
            shade = tuple(min(255, c + 30) for c in color)
            draw.line([(i, 0), (i, height)], fill=shade, width=1)
        
        # Cadre doré
        gold_color = (255, 215, 0)
        draw.rectangle([(15, 15), (width-15, height-15)], outline=gold_color, width=3)
        draw.rectangle([(25, 25), (width-25, height-25)], outline=gold_color, width=1)
        
        # Losange central
        center_x, center_y = width//2, height//2
        diamond_points = [
            (center_x, center_y - 50),
            (center_x + 70, center_y),
            (center_x, center_y + 50),
            (center_x - 70, center_y)
        ]
        draw.polygon(diamond_points, fill=gold_color, outline='white', width=2)
        
        # Texte premium
        self.draw_centered_text(draw, text, center_x, center_y, 28, color)
    
    def draw_centered_text(self, draw, text, x, y, size, color):
        """Dessiner du texte centré avec la meilleure police disponible"""
        try:
            # Essayer différentes polices système
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",  # macOS
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                "/Windows/Fonts/arial.ttf",  # Windows
                "C:/Windows/Fonts/arial.ttf"  # Windows alternative
            ]
            
            font = None
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, size)
                        break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
            
        except:
            font = ImageFont.load_default()
        
        # Calculer la position pour centrer le texte
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = x - text_width // 2
        text_y = y - text_height // 2
        
        # Effet d'ombre pour plus de profondeur
        shadow_offset = 2
        draw.text((text_x + shadow_offset, text_y + shadow_offset), text, 
                 fill=(0, 0, 0, 100), font=font)
        
        # Texte principal
        draw.text((text_x, text_y), text, fill=color, font=font)