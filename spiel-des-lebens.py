# -*- coding: utf-8 -*-
import time  # enthält eine Pause-Funktion
from random import randrange  # Zufallszahlen

import pygame  # Grafik
from pygame import locals  # Fenster-zu-Ereignis

try:  # Weiche Abhängigkeit: SenseHat
    from sense_hat import SenseHat  # Versuche import
except ImportError:
    SenseHat = lambda: None  # System hat keinen SenseHat


class Welt:
    farbe_lebendig = (255, 0, 0)
    farbe_tot = (255, 255, 255)

    def __init__(self, breite, höhe,
                 block_größe=None, lebendig=set()):
        """Setze die Eigenschaften eines neuen Objektes"""
        if block_größe is None:
            block_größe = min(9, 800//min(breite, höhe)) or 1
        self.breite = breite
        self.höhe = höhe
        self.block = int(block_größe)
        self.lebendig = lebendig
        try:
            self.sense = SenseHat()
        except OSError:
            self.sense = None
        super().__init__()

    def zufallswelt(self, dichte=0.3):
        """
        Bevölkere die Welt zufällig.
        Dichte gibt die Anteil der lebendigen Zellen an
        """
        n = int(dichte * self.breite * self.höhe)
        self.lebendig = set()
        while len(self.lebendig) < n:  # Wiederhole solange Zellen fehlen
            zelle = (randrange(self.breite),  # Zufällige X-Koordinate
                     randrange(self.höhe))     # Zufällige Y-Koordinate
            self.lebendig.add(zelle)  # zur Liste lebendiger Zellen hinzufügen

    def zeige(self, fenster):
        """Zeichne die Welt in einem pygame-Fenster"""
        pygame.draw.rect(fenster, self.farbe_tot,
            [0, 0, self.breite*self.block, self.höhe*self.block])
        for zelle in self.lebendig:  # Erst Hintergrund
            x, y = zelle             # dann alle lebendigen Zellen
            pygame.draw.rect(fenster, self.farbe_lebendig,
                             pygame.Rect(x*self.block, y*self.block,
                                         self.block-1, self.block-1))
        pygame.display.update()      # und anzeigen

    def zeige_auf_sensehat(self):
        """Zeige die Welt mit SenseHat-Leuchtdioden (nur Raspberry Pi)"""
        if self.sense is not None:
            sense.clear(farbe_tot)
            for zelle in self.lebendig:
                x, y = zelle
                if 0 <= x < 8 and 0 <= y < 8:
                    sense.set_pixel(zelle[0], zelle[1]. farbe_lebendig)

    def lebendige_nachbarn(self, zelle):
        """Zähle die Anzahl der lebendigen Nachbarn einer Zelle"""
        x, y = zelle  # Hole Koordinaten aus zelle
        return (((x-1, y+1) in self.lebendig) +
                ((x, y+1) in self.lebendig) +
                ((x+1, y+1) in self.lebendig) +
                ((x+1, y) in self.lebendig) +
                ((x+1, y-1) in self.lebendig) +
                ((x, y-1) in self.lebendig) +
                ((x-1, y-1)in self.lebendig) +
                ((x-1, y)in self.lebendig)
                )

    def zyklus(self):
        """Wende die Game of Life-Regeln einmal an"""
        neu = self.lebendig.copy()  # Kopie erstellen
        for zelle in self.lebendig:  # Alle lebendigen Zellen durchgehen
            anzahl = self.lebendige_nachbarn(zelle)
            if anzahl < 2 or anzahl > 3:    # Vereinsamung oder Überbevölkerung
                neu.remove(zelle)  # Stirbt - aus der Liste der Lebendigen entfernen
            # Prüfe alle Nachbarn einer lebendigen Zelle
            # wenn diese genau drei Nachbarn hat, muss sie evtl.
            # lebendig werden
            x, y = zelle
            if self.lebendige_nachbarn((x-1, y+1)) == 3:
                neu.add((x-1, y+1))
            if self.lebendige_nachbarn((x, y+1)) == 3:
                neu.add((x, y+1))
            if self.lebendige_nachbarn((x+1, y+1)) == 3:
                neu.add((x+1, y+1))
            if self.lebendige_nachbarn((x+1, y)) == 3:
                neu.add((x+1, y))
            if self.lebendige_nachbarn((x+1, y-1)) == 3:
                neu.add((x+1, y-1))
            if self.lebendige_nachbarn((x, y-1)) == 3:
                neu.add((x, y-1))
            if self.lebendige_nachbarn((x-1, y-1)) == 3:
                neu.add((x-1, y-1))
            if self.lebendige_nachbarn((x-1, y)) == 3:
                neu.add((x-1, y))
        self.lebendig = neu


welt_größe = 100
w = Welt(welt_größe, welt_größe)
pygame.init()  # Grafik initialisieren
bild = pygame.display.set_mode((w.block*w.breite, w.block*w.höhe))  # Grafikfenster öffnen
w.zufallswelt()  # zufällig lebendige Zellen hinzufügen
w.zeige(bild)  # Welt im Grafikfenster zeigen
while w.lebendig:
    time.sleep(0.2)  # Kurze Pause
    w.zyklus()  # eine Generation weiter
    w.zeige(bild)  # Anzeigen
    w.zeige_auf_sensehat()  # SenseHat
    if pygame.event.peek(locals.QUIT):  # Wenn das Fenster geschlossen wird
        break  # Beende die While-Schleife
pygame.display.quit()  # Schließe Fenster
pygame.quit()  #  Beende pygame-Grafik