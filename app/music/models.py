import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from datetime import datetime

STYLES = (
        ("Indie", "Indie"),
        ("Pop", "Pop"),
        ("Rock", "Rock"),
        ("Funky", "Funky"),
        ("Reggaeton", "Reggaeton"),
        ("Classic", "Classic"),
        ("Orquestra", "Orquestra"),
        ("Folk", "Folk")
    )

def less_than_five(value):
    """Raire an error if the value is 5 or greater."""
    if value >= 5:
        raise ValidationError("The price must be lower than 5 euros.")


def get_current_year():
    """Return the current year."""
    return datetime.today().year

def nine_pm():
    return datetime.strptime('09:00:00', '%H:%M:%S').time()


def fourteen_pm():
    return datetime.strptime('14:00:00', '%H:%M:%S').time()


class ValidatedModel(models.Model):
    """Automatically validate the model."""

    def save(self, *args, **kwargs):
        """Call validation on save."""
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        """Metadata."""

        abstract = True


class Author(ValidatedModel):
    """The Author model."""

    name = models.CharField(max_length=255)
    website = models.URLField(null=True, blank=True)
    first_appearance = models.SmallIntegerField(
        null=True, blank=True, verbose_name="Year of first appearance",
        validators=[MinValueValidator(1000), MaxValueValidator(get_current_year)]
    )
    last_appearance = models.SmallIntegerField(
        null=True, blank=True, verbose_name="Year of last appearance",
        validators=[MinValueValidator(1000), MaxValueValidator(get_current_year)]
    )

    def clean(self):
        """Validate the object."""
        if (self.first_appearance and self.last_appearance
                and self.first_appearance > self.last_appearance):
            raise ValidationError("The year of first appearance must be equal or "
                                  "lower to the year of last appearance.")


class Musician(ValidatedModel):
    """The Musician model."""

    INSTRUMENTS = (
        ("piano", "Piano"),
        ("eguitar", "Electric Guitar"),
        ("cguitar", "Classical Guitar"),
        ("aguitar", "Acoustic Guitar"),
        ("ebass", "Electric Bass"),
        ("bass", "Bass"),
        ("drums", "Drums"),
        ("voice", "Voice"),
        ("violin", "Violin"),
        ("harp", "Harp"),
        ("handpan", "Handpan"),
        ("tambourine", "Tambourine"),
        ("sax", "Saxophone"),
        ("trumpet", "Trumpet"),
        ("trombone", "Trombone"),
        ("flute", "Flute"),
        ("clarinet", "Clarinet"),
        ("ukulele", "Ukulele"),
    )

    name = models.CharField(max_length=150)
    nationality = models.CharField(max_length=2)
    instrument = models.CharField(max_length=25, choices=INSTRUMENTS)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="members")


class Album(ValidatedModel):
    """The Album model."""

    title = models.CharField(max_length=255)
    year_of_release = models.SmallIntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(get_current_year)]
    )
    produced_by = models.CharField(max_length=255, null=True, blank=True)


class Song(ValidatedModel):
    """The Song model."""

    audio = models.FileField(upload_to="audio")
    title = models.CharField(max_length=250)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL,
                               db_index=True, null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE,
                              max_length=250, null=True, blank=True)
    duration = models.DurationField()
    style = models.CharField(max_length=20, choices=STYLES, null=True, blank=True)
    playbacks = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=4, default=0,
                                validators=[less_than_five])
    deal_of_the_day = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                on_delete=models.SET_NULL, 
                                null=True, blank=True, 
                                related_name = 'created_by_user')
    
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                        on_delete=models.SET_NULL, 
                                        null=True, blank=True, 
                                        related_name = 'modified_by_user')

    class Meta:
        """Metadata."""

        constraints = [
            models.UniqueConstraint(fields=["title", "author", "album", "duration"],
                                    name="unique_song")
        ]

class Profile(ValidatedModel):
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    daily_start_time = models.TimeField(default=nine_pm)
    daily_finish_time = models.TimeField(default=fourteen_pm)
    preferred_style = models.CharField(max_length=20, choices=STYLES)
    preferred_song = models.ForeignKey(Song, on_delete= models.SET_NULL, null=True, blank=True)






# Task 2

"""
1. 
from django.contrib.auth.models import User

User.objects.all().values('username','profile__preferred_style','profile__preferred_song')
"""

"""
2. 
In [1]: from django.contrib.auth.models import User

In [2]: from music.models import Profile, Song, Album, Musician, Author

In [3]: superadmin_user = User.objects.get(username='superadmin')

In [4]: Song.objects.all().update(created_by=superadmin_user, last_modified_by=superadmin_user)
Out[4]: 791
"""

"""
3.

In [19]: josephine = Profile.objects.get(user__username='josephine')

In [20]: songs = Song.objects.filter(style=josephine.preferred_style)

In [21]: songs
Out[21]: <QuerySet [<Song: Song object (2)>, <Song: Song object (9)>, <Song: Song object (11)>, <Song: Song object (14)>, <Song: Song object (16)>, <Song: Song object (17)>, <Song: Song object (21)>, <Song: Song object (29)>, <Song: Song object (39)>, <Song: Song object (49)>, <Song: Song object (54)>, <Song: Song object (55)>, <Song: Song object (61)>, <Song: Song object (63)>, <Song: Song object (74)>, <Song: Song object (78)>, <Song: Song object (81)>, <Song: Song object (83)>, <Song: Song object (87)>, <Song: Song object (88)>, '...(remaining elements truncated)...']>
"""

"""
4. 


In [19]: tambourine_players = Musician.objects.filter(instrument='tambourine')

In [20]: id_lst = []

In [21]: for player in tambourine_players:
    ...:     id_lst.append(player.author.id)
    ...: 

In [22]: Song.objects.filter(author_id__in = id_lst).values('created_by__profile__preferred_style').distinct()
Out[22]: <QuerySet [{'created_by__profile__preferred_style': 'Indie'}, {'created_by__profile__preferred_style': 'Pop'}, {'created_by__profile__preferred_style': 'Rock'}, {'created_by__profile__preferred_style': 'Funky'}]>

"""

"""
5.

In [68]: between_1910_1919_ukulele = Musician.objects.filter(Q(instrument='ukulele') & Q(author__last_appearance__gte=1910) & Q(author__last_appearance__lte=1919))

In [69]: between_1980_1989_piano = Musician.objects.filter(Q(instrument='piano') & Q(author__first_appearance__gte=1980) & Q(author__first_appearance__lte=1989))

In [70]: ukulele_ids = []

In [71]: piano_ids = []

In [72]: for musician in between_1980_1989_piano:
    ...:     piano_ids.append(musician.author.id)
    ...: 

In [73]: for musician in between_1910_1919_ukulele:
    ...:     ukulele_ids.append(musician.author.id)
    ...: 

Song.objects.filter(Q(author_id__in= ukulele_ids)|Q(author_id__in = piano_ids)).values('created_by__profile__preferred_song', 'created_by__profile__preferred_song__title').distinct()
Out[82]: <QuerySet [{'created_by__profile__preferred_song': 2, 'created_by__profile__preferred_song__title': 'Audio number 3'}, {'created_by__profile__preferred_song': 3, 'created_by__profile__preferred_song__title': 'Audio number 4'}, {'created_by__profile__preferred_song': 44, 'created_by__profile__preferred_song__title': 'Audio number 2'}]>

"""