import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


ORGANIZATION_TYPES = [
	('MINISTRY', 'MINISTRY'),
	('HOSPITAL', 'HOSPITAL'),
	('PRODUCER', 'PRODUCER'),
	('BANK', 'BANK'),
	('OTHER', 'OTHER')
]


class Organization(models.Model):
	name = models.CharField(max_length=1024, null=False, blank=False)
	group = models.CharField(max_length=32, choices=ORGANIZATION_TYPES, null=False, blank=False, default='OTHER')
	key = models.CharField(null=True, blank=True, max_length=2056, default=None)

	def save(self, *args, **kwargs):
		if not self.id:
			if self.group == 'HOSPITAL':
				key_prefix = 'Ho'
			elif self.group == 'PRODUCER':
				key_prefix = 'Co'
			elif self.group == 'BANK':
				key_prefix = 'Ba'
			else:
				key_prefix = 'Mi'

		super(Organization, self).save(*args, **kwargs)
		self.key = key_prefix + str(self.id)
		return super(Organization, self).save(*args, **kwargs)

	def __str__(self):
		return '[Name: {} | Group: {} | Key: {}]'.format(self.name, self.group, self.key)


class OrganizationUser(AbstractUser):
	organization = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
	key = models.CharField(null=True, blank=True, max_length=2056, default=None)

	def save(self, *args, **kwargs):
		self.key = uuid.uuid1()
		return super(OrganizationUser, self).save(*args, **kwargs)

	def __str__(self):
		return '[Username: {} | Org: {} | Key: {}]'.format(self.username, self.organization, self.key)


class HospitalOrder(models.Model):
	id = models.CharField(null=False, blank=False, max_length=2056, primary_key=True)
	hospital = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)

	def __str__(self):
		return '[ID: {} | Hospital: {}]'.format(self.id, self.hospital)


class MinistryOrder(models.Model):
	id = models.CharField(null=False, blank=False, max_length=2056, primary_key=True)
	ministry = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)

	def __str__(self):
		return '[ID: {} | Ministry: {}]'.format(self.id, self.ministry)


class Deal(models.Model):
	id = models.CharField(null=False, blank=False, max_length=2056, primary_key=True)
	producer = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
	letter = models.CharField(null=False, blank=False, max_length=2056)

	def __str__(self):
		return '[ID: {} | Producer: {} | Letter: {}]'.format(self.id, self.producer, self.letter)


class Delivery(models.Model):
	id = models.CharField(null=False, blank=False, max_length=2056, primary_key=True)
	producer = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)

	def __str__(self):
		return '[ID: {} | Producer: {}]'.format(self.id, self.producer)


class PaymentLetter(models.Model):
	id = models.CharField(null=False, blank=False, max_length=2056, primary_key=True)
	bank = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
	order = models.CharField(null=True, max_length=2056)

	def __str__(self):
		return '[ID: {}]'.format(self.id)


class ProducerOffer(models.Model):
	id = models.CharField(null=False, blank=False, max_length=2056, primary_key=True)
	producer = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
	order = models.CharField(null=False, blank=False, max_length=2056)


class Payment(models.Model):
	order = models.CharField(null=False, blank=False, max_length=2056)
	price = models.DecimalField(null=False, blank=False, max_digits=9, decimal_places=2)
	producer = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
