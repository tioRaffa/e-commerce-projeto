class Base(models.Model):
    create = models.DateField(auto_now_add=True)
    update = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
        
        
class Services(Base):
    ICON_CHOICES = (
        ('lni-cog', 'engrenagem'),
        ('lni-stats-up', 'grafico'),
        ('ni-users', 'users'),
        ('lni-layers', 'design'),
        ('lni-mobile', 'mobile'),
        ('lni-rocket', 'rocket'),
    )
    
    service = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    icon = models.CharField(max_length=12, choices=ICON_CHOICES)