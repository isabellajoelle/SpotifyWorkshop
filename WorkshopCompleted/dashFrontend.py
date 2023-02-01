# Dash Imports
import dash
from dash.dependencies import Input, Output, State
from dash import html
from dash import dcc

# Imports from Created Class and .env File
from trackStats import SpotifyAPI
from dotenv import load_dotenv
import os
import json

# Accessing Information from your .env file
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

app = dash.Dash()

app.layout = html.Div([

    html.H1("Track Analyzer"),

    html.Label('Track Name: '),
    dcc.Input(id='track_name', value=None, placeholder="Enter Track Name", debounce=True, type='text'),

    html.Label('Artist Name: '),
    dcc.Input(id='artist_name', value=None, placeholder="Enter Artist Name", debounce=True, type='text'),

    html.Button(id='submit-button', type='submit', children='Submit'),

    html.Div(id='output')
])

@app.callback(
    Output("output", "children"),
    Input("track_name", "value"),
    Input("artist_name", "value"),
)

def on_click(track_name, artist_name):
        # Creating Client
        spotify = SpotifyAPI(client_id, client_secret)
        # Run Search
        search_data = spotify.search({"track": track_name, "artist": artist_name})
        print(len(search_data["tracks"]["items"]))
        if len(search_data["tracks"]["items"]) == 0:
            out = html.Div(
                id="centering",
                children=[
                    html.Div(
                        id="notFound",
                        className="card",                            
                        children=[
                            html.Div(
                                className="container",
                                children=[
                                    html.H4("This Track/Artist Does not Exist in Spotify's Database")
                                ]
                            )
                        ]
                    )
                ]
            )
            return out
        _id = search_data["tracks"]["items"][0]["id"]
        album_name = search_data["tracks"]["items"][0]["album"]["name"]
        art_name = search_data["tracks"]["items"][0]["artists"]
        artist_list = []
        for artist in art_name:
            artist_list += [artist["name"]]
        analysis_data = spotify.get_audio_analysis(_id)

        out = html.Div(
            id="updated_output",
            className="output",
            children=[
                html.Div(
                    id="main_div",
                    children=[
                        html.H2("Track: " + track_name),
                        html.H2("Artist: " + ", ".join(artist_list)),
                        html.H2("Album: " + album_name),
                    ]
                ),

                html.Div(
                    id="centering",
                    children=[
                        html.Div(
                            id="danceability",
                            className="card",
                            children=[
                                html.Div(
                                    className="container",
                                    children=[
                                        html.H3("Danceability: " + str(analysis_data["danceability"])),
                                        html.H6("Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable."),
                                    ]
                                )
                            ]
                        ),

                        html.Div(
                            id="energy",
                            className="card",
                            children=[
                                html.Div(
                                    className="container",
                                    children=[
                                        html.H3("Energy: " + str(analysis_data["energy"])),
                                        html.H6("Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy."),
                                    ]
                                )
                            ]
                        ),

                        html.Div(
                            id="loudness",
                            className="card",
                            children=[
                                html.Div(
                                    className="container",
                                    children=[
                                        html.H3("Loudness: " + str(analysis_data["loudness"])),
                                        html.H6("The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typically range between -60 and 0 db."),
                                    ]
                                )
                            ]
                        ),

                        html.Div(
                            id="valence",
                            className="card",
                            children=[
                                html.Div(
                                    className="container",
                                    children=[
                                        html.H3("Valence: " + str(analysis_data["valence"])),
                                        html.H6("A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry)."),
                                    ]
                                )
                            ]
                        ),

                        html.Div(
                            id="Acousticness",
                            className="card",
                            children=[
                                html.Div(
                                    className="container",
                                    children=[
                                        html.H3("Acousticness: " + str(analysis_data["acousticness"])),
                                        html.H6("A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic."),
                                    ]
                                )
                            ]
                        ),

                        html.Div(
                            id="liveness",
                            className="card",
                            children=[
                                html.Div(
                                    className="container",
                                    children=[
                                        html.H3("Liveness: " + str(analysis_data["liveness"])),
                                        html.H6("Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.")
                                    ]
                                )
                            ]
                        ),
                    ]
                ),
            ],
        )
        return out


if __name__ == '__main__':
    app.run_server(debug=True)