import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pymongo import MongoClient
from urllib.parse import quote_plus
import certifi
import warnings
from datetime import datetime
import numpy as np
import streamlit as st
#from page_link import create_sidebar_navigation, create_horizontal_navigation

warnings.filterwarnings("ignore")

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Data Never Lies",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)



#st.title("Trang phụ")
#create_sidebar_navigation()

# ========== CSS STYLING ==========
st.markdown("""
<style>
.team-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 15px;
    margin: 10px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    color: white;
    text-align: center;
}

.team-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.team-item {
    background: white;
    border-radius: 15px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 3px 20px rgba(0,0,0,0.08);
    border: 1px solid #f0f0f0;
    transition: all 0.4s ease;
    height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;
    overflow: hidden;
}

.team-item:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 35px rgba(102, 126, 234, 0.2);
    border-color: #667eea;
}

.team-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.05), transparent);
    transition: left 0.6s;
}

.team-item:hover::before {
    left: 100%;
}

.sidebar-title {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 25px;
    color: #2c3e50;
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.5px;
    position: relative;
    padding-bottom: 12px;
}

.sidebar-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 50px;
    height: 2.5px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 2px;
}

.competition-item {
    display: flex;
    align-items: center;
    margin: 6px 0;
    width: 100%;
}

.competition-logo {
    width: 32px;
    height: 32px;
    object-fit: contain;
    margin-right: 12px;
    flex-shrink: 0;
}

.competition-btn {
    display: flex;
    align-items: center;
    padding: 12px 15px;
    width: 100%;
    border: none;
    border-radius: 10px;
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    border: 1px solid #e9ecef;
    position: relative;
    overflow: hidden;
    font-size: 14px;
    font-weight: 500;
    color: #495057;
    text-align: left;
    justify-content: flex-start;
}

.competition-btn:hover {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
    border-color: #667eea;
}

.competition-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.5s;
}

.competition-btn:hover::before {
    left: 100%;
}

.league-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px;
    border-radius: 20px;
    text-align: center;
    margin: 30px 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    position: relative;
    overflow: hidden;
}

.league-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: float 6s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    50% { transform: translate(-20px, -20px) rotate(180deg); }
}

.stats-container {
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    padding: 30px;
    border-radius: 15px;
    margin: 25px 0;
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
    border: 1px solid #e9ecef;
}

.team-logo {
    width: 90px;
    height: 90px;
    object-fit: contain;
    margin: 15px auto;
    display: block;
    transition: transform 0.3s ease;
}

.team-item:hover .team-logo {
    transform: scale(1.1);
}

.selected-team-info {
    background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
    padding: 30px;
    border-radius: 18px;
    margin: 25px 0;
    color: #2c3e50;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border: 1px solid rgba(255,255,255,0.2);
}

.main-title {
    text-align: center;
    padding: 40px 0;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    border-radius: 20px;
    margin: 20px 0;
}

.main-title h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 3.5em;
    margin-bottom: 15px;
    font-weight: 800;
    letter-spacing: -1px;
}

.welcome-section {
    text-align: center;
    padding: 100px 30px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 25px;
    color: white;
    margin: 40px 0;
    position: relative;
    overflow: hidden;
}

.welcome-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
    animation: sparkle 20s linear infinite;
}

@keyframes sparkle {
    0% { transform: translateY(0); }
    100% { transform: translateY(-100px); }
}

.footer {
    text-align: center;
    color: #6c757d;
    padding: 30px 20px;
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    border-radius: 15px;
    margin-top: 40px;
    border-top: 3px solid #667eea;
}

/* Metric cards styling */
.metric-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    border-left: 4px solid #667eea;
    margin-bottom: 1rem;
    text-align: center;
}

.metric-value {
    font-size: 2.5em;
    font-weight: 700;
    color: #667eea;
    margin: 10px 0;
}

.metric-label {
    color: #6c757d;
    font-weight: 500;
}

/* Streamlit button override */
.stButton > button {
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%) !important;
    border: 2px solid #e9ecef !important;
    border-radius: 12px !important;
    padding: 12px 20px !important;
    transition: all 0.3s ease !important;
    font-weight: 600 !important;
    color: #495057 !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3) !important;
    border-color: #667eea !important;
}

/* Analysis sections */
.analysis-section {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin: 20px 0;
}

.analysis-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)



# ========== MongoDB CONNECTION  ==========
username = "lilduckhoa102"
password = "5pSgoZXMuomY8w8r"
cluster = "football-player-db.vk7ebjz.mongodb.net"
encoded_password = quote_plus(password)
uri = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?retryWrites=true&w=majority"

try:
    client = MongoClient(uri, tlsCAFile=certifi.where())
    client.admin.command("ping")
    db = client['fifa_database']
    teams_col = db["teams"]
    matches_col = db["matches"]
    players_col = db["player_data_for_leagues"]
    scores_col = db["scores"]
    leagues_col = db["leagues"]
    player_stats_col = db["player"]
    st.success(" Kết nối MongoDB thành công!")
except Exception as e:
    db = None
    st.error(f" Lỗi kết nối MongoDB: {e}")


# ========== các hàm lấy dữ liệu  ==========
@st.cache_data(ttl=300)
def get_team_statistics(team_id):
    """Lấy thống kê chi tiết của đội bóng với  Aggregation Pipeline """
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"home_team_id": team_id},
                    {"away_team_id": team_id}
                ]
            }
        },
        {
            "$lookup": {
                "from": "scores",
                "localField": "match_id",
                "foreignField": "match_id",
                "as": "score_info"
            }
        },
        {"$unwind": "$score_info"},
        {
            "$addFields": {
                "is_home": {"$eq": ["$home_team_id", team_id]},
                "goals_for": {
                    "$cond": [
                        {"$eq": ["$home_team_id", team_id]},
                        "$score_info.full_time_home",
                        "$score_info.full_time_away"
                    ]
                },
                "goals_against": {
                    "$cond": [
                        {"$eq": ["$home_team_id", team_id]},
                        "$score_info.full_time_away",
                        "$score_info.full_time_home"
                    ]
                },
                "result": {
                    "$cond": [
                        {
                            "$and": [
                                {"$eq": ["$home_team_id", team_id]},
                                {"$eq": ["$winner", "HOME_TEAM"]}
                            ]
                        },
                        "win",
                        {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$eq": ["$away_team_id", team_id]},
                                        {"$eq": ["$winner", "AWAY_TEAM"]}
                                    ]
                                },
                                "win",
                                {
                                    "$cond": [
                                        {"$eq": ["$winner", "DRAW"]},
                                        "draw",
                                        "loss"
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "total_matches": {"$sum": 1},
                "wins": {
                    "$sum": {
                        "$cond": [{"$eq": ["$result", "win"]}, 1, 0]
                    }
                },
                "draws": {
                    "$sum": {
                        "$cond": [{"$eq": ["$result", "draw"]}, 1, 0]
                    }
                },
                "losses": {
                    "$sum": {
                        "$cond": [{"$eq": ["$result", "loss"]}, 1, 0]
                    }
                },
                "goals_for": {"$sum": "$goals_for"},
                "goals_against": {"$sum": "$goals_against"},
                "home_matches": {
                    "$sum": {
                        "$cond": ["$is_home", 1, 0]
                    }
                },
                "away_matches": {
                    "$sum": {
                        "$cond": ["$is_home", 0, 1]
                    }
                }
            }
        },
        {
            "$addFields": {
                "goal_difference": {"$subtract": ["$goals_for", "$goals_against"]},
                "win_rate": {
                    "$multiply": [
                        {"$divide": ["$wins", "$total_matches"]},
                        100
                    ]
                },
                "points": {
                    "$add": [
                        {"$multiply": ["$wins", 3]},
                        "$draws"
                    ]
                },
                "avg_goals_per_match": {
                    "$divide": ["$goals_for", "$total_matches"]
                }
            }
        }
    ]
    
    result = list(matches_col.aggregate(pipeline))
    return result[0] if result else {}

@st.cache_data(ttl=300)
def get_teams_by_league(league_id):
    """Lấy danh sách đội bóng theo giải đấu """
    pipeline = [
        {
            "$match": {
                "league_id": league_id
            }
        },
        {
            "$lookup": {
                "from": "leagues",
                "localField": "league_id",
                "foreignField": "league_id",
                "as": "league_info"
            }
        },
        {
            "$unwind": "$league_info"
        },
        {
            "$project": {
                "_id": 0,
                "team_id": 1,
                "name": 1,
                "cresturl": 1,
                "founded_year": 1,
                "league_name": "$league_info.name",
                "country": "$league_info.country",
                "league_icon": "$league_info.icon_url"
            }
        }
    ]
    return list(teams_col.aggregate(pipeline))

@st.cache_data(ttl=300)
def get_team_players_advanced(team_id):
    """Lấy thống kê cầu thủ nâng cao với group và unwind"""
    
    pipeline = [
        {"$match": {"team_id": team_id}},
        {
            "$addFields": {
                "age": {
                    "$floor": {
                        "$divide": [
                            {"$subtract": [{"$dateFromString": {"dateString": "2023-12-31"}}, 
                                         {"$dateFromString": {"dateString": "$date_of_birth"}}]},
                            365.25 * 24 * 60 * 60 * 1000
                        ]
                    }
                }
            }
        },
        {
            "$group": {
                "_id": "$position",
                "players": {
                    "$push": {
                        "name": "$name",
                        "nationality": "$nationality",
                        "age": "$age",
                        "date_of_birth": "$date_of_birth"
                    }
                },
                "count": {"$sum": 1},
                "avg_age": {"$avg": "$age"},
                "nationalities": {"$addToSet": "$nationality"}
            }
        },
        {
            "$addFields": {
                "nationality_count": {"$size": "$nationalities"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    return list(players_col.aggregate(pipeline))

@st.cache_data(ttl=300)
def get_recent_matches_detailed(team_id, limit=10):
    """Lấy trận đấu gần nhất với thông tin chi tiết"""
    
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"home_team_id": team_id},
                    {"away_team_id": team_id}
                ]
            }
        },
        {
            "$lookup": {
                "from": "scores",
                "localField": "match_id",
                "foreignField": "match_id",
                "as": "score"
            }
        },
        {"$unwind": "$score"},
        {
            "$lookup": {
                "from": "teams",
                "localField": "home_team_id",
                "foreignField": "team_id",
                "as": "home_team"
            }
        },
        {
            "$lookup": {
                "from": "teams",
                "localField": "away_team_id",
                "foreignField": "team_id",
                "as": "away_team"
            }
        },
        {"$unwind": "$home_team"},
        {"$unwind": "$away_team"},
        {
            "$addFields": {
                "match_date": {"$dateFromString": {"dateString": "$utc_date"}},
                "is_home": {"$eq": ["$home_team_id", team_id]},
                "team_result": {
                    "$cond": [
                        {
                            "$and": [
                                {"$eq": ["$home_team_id", team_id]},
                                {"$eq": ["$winner", "HOME_TEAM"]}
                            ]
                        },
                        "W",
                        {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$eq": ["$away_team_id", team_id]},
                                        {"$eq": ["$winner", "AWAY_TEAM"]}
                                    ]
                                },
                                "W",
                                {
                                    "$cond": [
                                        {"$eq": ["$winner", "DRAW"]},
                                        "D",
                                        "L"
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        },
        {"$sort": {"match_date": -1}},
        {"$limit": limit},
        {
            "$project": {
                "_id": 0,
                "match_id": 1,
                "matchday": 1,
                "utc_date": 1,
                "home_team_name": "$home_team.name",
                "away_team_name": "$away_team.name",
                "home_score": "$score.full_time_home",
                "away_score": "$score.full_time_away",
                "winner": 1,
                "is_home": 1,
                "team_result": 1,
                "opponent": {
                    "$cond": [
                        "$is_home",
                        "$away_team.name",
                        "$home_team.name"
                    ]
                }
            }
        }
    ]
    
    return list(matches_col.aggregate(pipeline))

# ========== SIDEBAR  ==========
if "selected_competition" not in st.session_state:
    st.session_state.selected_competition = None
if "selected_team_detail" not in st.session_state:
    st.session_state.selected_team_detail = None

with st.sidebar:
    st.markdown('<div class="sidebar-title">🏆 Top League</div>', unsafe_allow_html=True)

    competitions = [
        {"name": "Premier League", "logo": "https://vinsport.vn/wp-content/uploads/2022/09/Logo-patch-badge-su-tu-EPL-giai-ngoai-hang-anh.png", "id": 1},
        {"name": "LaLiga", "logo": "https://1000logos.net/wp-content/uploads/2019/01/Spanish-La-Liga-Logo.png", "id": 3},
        {"name": "Bundesliga", "logo": "https://assets.website-files.com/5ee732bebd9839b494ff27cd/5f0c75aadbd7ec8c9ebdc48c_1200px-Bundesliga_logo_(2017).svg.png", "id": 4},
        {"name": "Serie A", "logo": "https://www.liblogo.com/img-logo/se1113s3c3-serie-a-logo-serie-a-logos-vector-in-svg-eps-ai-cdr-pdf-free-download.png", "id": 2},
        {"name": "Ligue 1", "logo": "https://crests.football-data.org/FL1.png", "id": 5},
        {"name": "V-League 1", "logo": "https://cdn.haitrieu.com/wp-content/uploads/2022/03/logo-v-league-1-original-1020x1024.png", "id": 10},
        {"name": "UEFA Champions League", "logo": "https://clipground.com/images/champions-league-logo-png-9.png", "id": 11},
        {"name": "UEFA Europa League", "logo": "https://logospng.org/download/uefa-europa-league/logo-uefa-europa-league-1024.png", "id": 12}
    ]

    for comp in competitions:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            try:
                st.image(comp["logo"], width=40)
            except:
                st.write("")
        with col2:
            if st.button(comp["name"], key=comp["name"], use_container_width=True):
                st.session_state.selected_competition = comp
                st.session_state.selected_team_detail = None  # Reset team selection

                    # ========== Thanh tìm kiếm cầu thủ  ==========
    






                                            # ========== MAIN CONTENT ==========
if st.session_state.selected_competition:
    comp = st.session_state.selected_competition
    
    # Header đẹp cho giải đấu 
    st.markdown(f"""
    <div class="league-header">
        <h2 style="font-size: 2.5em; margin-bottom: 10px; font-weight: 700;">{comp['name']}</h2>
        <p style="font-size: 1.2em; opacity: 0.9;">Khám phá các đội bóng và phân tích chuyên sâu</p>
    </div>
    """, unsafe_allow_html=True)

    # Lấy dữ liệu đội bóng
    with st.spinner(f"Đang tải danh sách đội bóng từ {comp['name']}..."):
        teams = get_teams_by_league(comp["id"])
    
    if teams:
        # Thống kê tổng quan 
        st.markdown(f"""
        <div class="stats-container">
            <h3 style="color: #2c3e50; margin-bottom: 25px; font-weight: 600;"> Thống kê tổng quan</h3>
            <div style="display: flex; justify-content: space-around; text-align: center;">
                <div style="padding: 20px;">
                    <h2 style="color: #667eea; margin: 0; font-size: 2.5em; font-weight: 700;">{len(teams)}</h2>
                    <p style="margin: 8px 0; color: #6c757d; font-weight: 500;">Đội bóng</p>
                </div>
                <div style="padding: 20px;">
                    <h2 style="color: #667eea; margin: 0; font-size: 2.5em; font-weight: 700;">{teams[0]['country'] if teams else 'N/A'}</h2>
                    <p style="margin: 8px 0; color: #6c757d; font-weight: 500;">Quốc gia</p>
                </div>
                <div style="padding: 20px;">
                    <h2 style="color: #667eea; margin: 0; font-size: 1.8em; font-weight: 700;">{teams[0]['league_name'] if teams else 'N/A'}</h2>
                    <p style="margin: 8px 0; color: #6c757d; font-weight: 500;">Giải đấu</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Hiển thị dạng lưới 
        st.markdown("### ⚽ Chọn đội để xem phân tích chi tiết")
        
        cols_per_row = 4
        for i in range(0, len(teams), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, team in enumerate(teams[i:i+cols_per_row]):
                with cols[j]:
                    if st.button(
                        f"{team['name']}", 
                        key=f"team_{team.get('team_id', i*cols_per_row+j)}",
                        use_container_width=True
                    ):
                        st.session_state.selected_team_detail = team
                    
                    # Hiển thị card info 
                    st.markdown(f"""
                    <div class="team-item">
                        <img src="{team.get('cresturl', '')}" class="team-logo" onerror="this.src='https://via.placeholder.com/90x90?text=Logo'">
                        <h4 style="margin: 15px 0 8px 0; color: #2c3e50; font-weight: 600;">{team['name']}</h4>
                        <p style="color: #6c757d; font-size: 0.9em; margin: 0;">ID: {team.get('team_id', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                  
            # ================================ TEAM DETAILS SECTION =======================================
if st.session_state.selected_team_detail:
    team = st.session_state.selected_team_detail
    team_id = team.get('team_id')
    
    st.markdown("---")
    
    # Team Header
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(team.get('cresturl', ''), width=100)
    with col2:
        st.markdown(f"""
        <div style="padding: 20px 0;">
            <h2 style="color: #2c3e50; margin-bottom: 10px;">{team['name']}</h2>
            <p style="color: #6c757d;">Thành lập: {team.get('founded_year', 'N/A')} | ID: {team_id}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Get team statistics
    with st.spinner("Đang tải thống kê đội bóng..."):
        team_stats = get_team_statistics(team_id)
    
    if team_stats:
        # Statistics Display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{team_stats.get('total_matches', 0)}</div>
                <div class="metric-label">Tổng trận</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #28a745;">{team_stats.get('wins', 0)}</div>
                <div class="metric-label">Thắng</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #ffc107;">{team_stats.get('draws', 0)}</div>
                <div class="metric-label">Hòa</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #dc3545;">{team_stats.get('losses', 0)}</div>
                <div class="metric-label">Thua</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Goals and Performance
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #17a2b8;">{team_stats.get('goals_for', 0)}</div>
                <div class="metric-label">Bàn thắng</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #fd7e14;">{team_stats.get('goals_against', 0)}</div>
                <div class="metric-label">Bàn thua</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            goal_diff = team_stats.get('goal_difference', 0)
            diff_color = "#28a745" if goal_diff >= 0 else "#dc3545"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {diff_color};">{goal_diff:+d}</div>
                <div class="metric-label">Hiệu số</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #6f42c1;">{team_stats.get('points', 0)}</div>
                <div class="metric-label">Điểm</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Player Analysis
    with st.spinner("Đang tải thông tin cầu thủ..."):
        player_stats = get_team_players_advanced(team_id)
    
    if player_stats:
        st.markdown("###  Thông tin cầu thủ")
        
        # Position breakdown
        total_players = sum([pos['count'] for pos in player_stats])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Position distribution
            positions = []
            counts = []
            for pos_data in player_stats:
                if pos_data['_id']:  # Skip null positions
                    positions.append(pos_data['_id'])
                    counts.append(pos_data['count'])
            
            if positions:
                fig_pie = px.pie(
                    values=counts, 
                    names=positions,
                    title="Phân bố vị trí cầu thủ",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_layout(height=300, showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        


        
        # Team summary
        total_nationalities = len(set([nat for pos in player_stats for nat in pos.get('nationalities', [])]))
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                     padding: 20px;border-radius: 12px;margin: 20px 0;">
            <h4 style="color: #1565c0;margin-bottom: 15px;">Tổng quan đội hình</h4>
            <div style="display: flex; justify-content: space-around;text-align: center;">
                <div>
                    <h3 style="color: #1976d2; margin: 0;">{total_players}</h3>
                    <p style="margin: 5px 0; color: #424242;">Tổng cầu thủ</p>
                </div>
                <div>
                    <h3 style="color: #1976d2; margin: 0;">{total_nationalities}</h3>
                    <p style="margin: 5px 0; color: #424242;">Quốc tịch</p>
                </div>
                <div>
                    <h3 style="color: #1976d2; margin: 0;">{len(player_stats)}</h3>
                    <p style="margin: 5px 0; color: #424242;">Vị trí</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed player information by position
        st.markdown("### Danh sách cầu thủ chi tiết")
        
        for pos_data in player_stats:
            if pos_data['_id'] and pos_data['players']:
                position = pos_data['_id']
                players = pos_data['players']
                
                with st.expander(f"🏃 {position} ({len(players)} cầu thủ)", expanded=False):
                    # Create dataframe for better display
                    player_df = pd.DataFrame(players)
                    
                    if not player_df.empty:
                        player_df.index = pd.RangeIndex(1, len(player_df) + 1)

                        # Rename columns for Vietnamese
                        column_mapping = {
                            'name': 'Tên cầu thủ',
                            'nationality': 'Quốc tịch', 
                            'age': 'Tuổi',
                            'date_of_birth': 'Ngày sinh'
                        }
                        
                        # Only show existing columns
                        available_columns = [col for col in column_mapping.keys() if col in player_df.columns]
                        display_df = player_df[available_columns].rename(columns=column_mapping)
                        
                        # Format date of birth if exists
                        if 'Ngày sinh' in display_df.columns:
                            display_df['Ngày sinh'] = pd.to_datetime(display_df['Ngày sinh'], errors='coerce').dt.strftime('%d/%m/%Y')

                        
                        # Display the dataframe
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            hide_index=False
                        )
                        
                        # Position statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            avg_age = round(pos_data.get('avg_age', 0), 1)
                            st.metric("Tuổi trung bình", f"{avg_age} tuổi")
                        
                        with col2:
                            nationality_count = len(pos_data.get('nationalities', []))
                            st.metric("Số quốc tịch", nationality_count)
                        
                        with col3:
                            st.metric("Tổng cầu thủ", len(players))
                        
                        # Show top nationalities for this position
                        if pos_data.get('nationalities'):
                            nationality_list = ", ".join(pos_data['nationalities'][:5])
                            if len(pos_data['nationalities']) > 5:
                                nationality_list += f" và {len(pos_data['nationalities']) - 5} quốc tịch khác"
                            
                            st.markdown(f"""
                            <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; margin-top: 10px;">
                                <strong> Quốc tịch:</strong> {nationality_list}
                            </div>
                            """, unsafe_allow_html=True)
    
    else:
        st.info("Không có dữ liệu cầu thủ cho đội này.")

else:
    # Welcome message when no team is selected
    st.markdown("""
    <div class="welcome-section">
        <h2 style="font-size: 2.5em; margin-bottom: 20px; font-weight: 700;">Chào mừng đến với Football Analytics!</h2>
        <p style="font-size: 1.3em; opacity: 0.9; margin-bottom: 30px;">Chọn một giải đấu và đội bóng để bắt đầu khám phá</p>
        <div style="font-size: 4em; margin: 30px 0;"></div>
    </div>
    """, unsafe_allow_html=True)



