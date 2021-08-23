"""empty message

Revision ID: 2da6bd60d8c3
Revises: bff68c5371ed
Create Date: 2021-08-20 19:03:06.592253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers', 'used by Alembic.
revision = '2da6bd60d8c3'
down_revision = 'bff68c5371ed'
branch_labels = None
depends_on = None

Venue_fields = [ 'name', 'city', 'state', 'address', 'phone', 'image_link', 'facebook_link', 'genres', 'looking_talent', 'seeking_description', 'website_link']
mock_Venue_data_list = [
    [ "'The Musical Hop'", "'San Francisco'",  "'CA'",   "'1015 Folsom Street'", "'123-123-1234'", "'https://image'", "'https://www.facebook.com/TheMusicalHop'", "'JAZZ, REGGAE, SWING, CLASSICAL, FOLK'", "true", "''", "'https://www.themusicalhop.com'", ],
    [ "'Park Square Live Park Square Music & Coffee'", "'San Francisco'",  "'CA'",   "'34 Whiskey Moore Ave'", "'415-000-1234'", "'https://image'", "'https://www.facebook.com/ParkSquareLiveMusicAndCoffee'", "'Rock'", "false", "''", "'https://www.parksquarelivemusicandcoffee.com'", ],
    [ "'The Dueling Pianos Bar'", "'New York'",  "'NY'",   "'335 Delancey Street'", "'914-003-1132'", "'https://image'", "'https://www.facebook.com/theduelingpianos'", "'Classical, R&B, Hip-Hop'", "false", "''", "'https://www.theduelingpianos.com'", ],
]

Artist_fields = [ 'name', 'city', 'state', 'phone', 'looking_venue', 'seeking_description', 'genres', 'image_link', 'website_link', 'facebook_link']
mock_Artist_data_list = [
    [ "'Guns N Petals'", "'San Francisco'",  "'CA'",   "'326-123-5000'", "true", "'Looking for shows to perform at in the San Francisco Bay Area!'", "'Rock N Roll'", "'https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80'", "'https://www.gunsnpetalsband.com'", "'https://www.facebook.com/GunsNPetals'", ],
    [ "'Matt Quevedo'", "'New York'",  "'NY'",   "'300-400-5000'", "false", "''", "'Jazz'", "'https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80'", "null", "'https://www.facebook.com/mattquevedo923251523'", ],
    [ "'The Wild Sax Band'", "'San Francisco'",  "'CA'",   "'432-325-5432'", "false", "''", "'Jazz, Classical'", "'https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80'", "null", "null", ],
]

Show_fields         = [ 'artist_id', 'venue_id', 'start_datetime' ]
mock_Show_fields    = [
    [ "1", "1", "'2019-05-21T21:30:00.000Z'"],
    [ "2", "2", "'2019-06-15T23:00:00.000Z'"],
    [ "3", "2", "'2035-04-01T20:00:00.000Z'"],
    [ "3", "2", "'2035-04-08T20:00:00.000Z'"],
    [ "3", "2", "'2035-04-15T20:00:00.000Z'"],   
]

def build_INSERT_SQL_str(sql_table, sql_fields, sql_values_list):
    assert(len(sql_fields) == len(sql_values_list))
    Data_entry_str = '{}, ' * (len(sql_fields) - 1) + '{}'
    values_str = ", ".join(sql_values_list)
    INSERT_Str_template = 'INSERT INTO {} ({}) VALUES({{}})'.format(sql_table, Data_entry_str) #sql_table, Data_entry_str
    sql_args = sql_fields + [values_str,]
    return INSERT_Str_template.format(*sql_args)

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.execute('DELETE FROM "Show"')
    op.execute('DELETE FROM "Venue"')
    op.execute('DELETE FROM "Artist"')

    op.execute('ALTER SEQUENCE "Venue_id_seq" RESTART WITH 1')
    op.execute('ALTER SEQUENCE "Artist_id_seq" RESTART WITH 1')
    op.execute('ALTER SEQUENCE "Show_id_seq" RESTART WITH 1')
    
    # insert Venue's mock data
    for venue_values in mock_Venue_data_list:
        INSERT_Venue_Str_template = build_INSERT_SQL_str('"Venue"', Venue_fields, venue_values)
        op.execute(INSERT_Venue_Str_template)

    # insert Artist's mock data
    for art_values in mock_Artist_data_list:
        INSERT_Artist_Str_template = build_INSERT_SQL_str('"Artist"', Artist_fields, art_values)
        op.execute(INSERT_Artist_Str_template)

    # insert Show's mock data
    for show_values in mock_Show_fields:
        INSERT_Show_Str_template = build_INSERT_SQL_str('"Show"', Show_fields, show_values)
        op.execute(INSERT_Show_Str_template)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('DELETE FROM "Show"')
    op.execute('DELETE FROM "Venue"')
    op.execute('DELETE FROM "Artist"')
    # ### end Alembic commands ###