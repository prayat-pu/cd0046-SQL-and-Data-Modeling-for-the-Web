INSERT INTO public."Artist"(
	id, name, city, state, phone, genres, image_link, facebook_link, website_link, looking_for_venues, seeking_description)
	VALUES (1, 'Guns N Petals', 'San Francisco', 'CA', '326-123-5000',
			ARRAY ['Rock n Roll'], 
			'https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80',
			'https://www.facebook.com/GunsNPetals',
			'https://www.gunsnpetalsband.com',
			true, 'Looking for shows to perform at in the San Francisco Bay Area!'),
			(2, 'Matt Quevedo', 'New York', 'NY', '300-400-5000',
			 ARRAY ['JAZZ'],
			 'https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80',
			 'https://www.facebook.com/mattquevedo923251523',
			 '',
			 false, ''),
			(3, 'The Wild Sax Band', 'San Francisco', 'CA', '432-325-5432',
			 ARRAY ['Jazz', 'Classical'],
			 'https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80',
			 '','',false,'');