INSERT INTO public."Venue"(
	id, name, city, state, address, phone, image_link, facebook_link, website_link,
	"looking_for_Talent", seeking_description, genres)
	VALUES (2, 'The Dueling Pianos Bar', 'New York', 'NY', '335 Delancey Street', '914-003-1132', 
			'https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80',
			'https://www.facebook.com/theduelingpianos',
			'https://www.theduelingpianos.com',
			false, '',
			ARRAY ['Classical', 'R&B', 'Hip-Hop']),
			(3, 'Park Square Live Music & Coffee', 'San Francisco', 'CA', '34 Whiskey Moore Ave', '415-000-1234',
			 'https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80',
			 'https://www.facebook.com/ParkSquareLiveMusicAndCoffee',
			 'https://www.parksquarelivemusicandcoffee.com',
			false, '', ARRAY ['Rock n Roll', 'Jazz', 'Classical', 'Folk']);