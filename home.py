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

warnings.filterwarnings("ignore")

# Phải đặt page config đầu tiên
st.set_page_config(
    page_title="FIFA Player Radar Chart", 
    layout="wide",
    page_icon="⚽"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding-top: 2rem;
    }
    
    /* Custom header styling */
    .custom-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .custom-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .custom-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(145deg, #f8f9ff, #ffffff);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e8ecf3;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    /* Enhanced Sidebar Styling */
    .css-1d391kg, .css-17eq0hr {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%) !important;
        border-right: 3px solid #667eea !important;
    }
    
    /* Sidebar content */
    .css-pkbazv {
        background: transparent !important;
        color: white !important;
    }
    
    /* Stats info box */
    .stats-info {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    }
    
    /* Player info card */
    .player-info {
        background: linear-gradient(145deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid #ffffff;
        margin: 1rem 0;
    }
    
    .player-info h3 {
        color: white !important;
        margin-bottom: 1rem;
    }
    
    .player-info p {
        color: white !important;
        margin: 0.5rem 0;
    }
    
    .player-info strong {
        color: #f0f0f0 !important;
    }
    
    /* Top skills styling */
    .top-skills-container {
        background: linear-gradient(145deg, #764ba2, #667eea);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
    
    .skill-item {
        background: rgba(255,255,255,0.1);
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.3rem 0;
        color: white;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Kết nối MongoDB Atlas
@st.cache_resource
def init_connection():
    """Khởi tạo kết nối MongoDB với error handling tốt hơn"""
    username = "lilduckhoa102"
    password = "5pSgoZXMuomY8w8r"
    cluster = "football-player-db.vk7ebjz.mongodb.net"
    encoded_password = quote_plus(password)
    uri = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?retryWrites=true&w=majority"
    
    try:
        client = MongoClient(
            uri, 
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,  # Timeout sau 5 giây
            connectTimeoutMS=10000,         # Connection timeout
            socketTimeoutMS=20000           # Socket timeout
        )
        # Test the connection
        client.admin.command("ping")
        db = client['fifa_database']
        
        return db
    except Exception as e:
        st.error(f" Lỗi kết nối MongoDB: {e}")
        st.info("Kiểm tra lại:")
        st.info("- Thông tin đăng nhập MongoDB")
        st.info("- Kết nối internet")
        st.info("- IP whitelist trong MongoDB Atlas")
        return None

@st.cache_data
def load_data():
    """Load dữ liệu từ MongoDB với error handling"""
    db = init_connection()
    if db is None:
        return pd.DataFrame()
    
    try:
        player_col = db['players']
        
        # Kiểm tra xem collection có tồn tại không
        if 'players' not in db.list_collection_names():
            st.error(" Collection 'players' không tồn tại trong database")
            return pd.DataFrame()
        
        # Truy vấn MongoDB để lấy dữ liệu cầu thủ (tối ưu hóa để tránh memory limit)
        pipeline = [
            {
                "$match": {
                    "name": {"$exists": True, "$ne": None},
                    "general_stats.overall_rating": {"$exists": True, "$ne": None, "$gte": 50}  # Chỉ lấy cầu thủ có rating >= 50
                }
            },
            {
                "$project": {
                    "name": 1,
                    "overall_rating": "$general_stats.overall_rating",
                    "positions": "$personal_info.positions",
                    # Attack skills
                    "crossing": "$attack_skills.crossing",
                    "finishing": "$attack_skills.finishing",
                    "heading_accuracy": "$attack_skills.heading_accuracy",
                    "short_passing": "$attack_skills.short_passing",
                    "volleys": "$attack_skills.volleys",
                    "dribbling": "$attack_skills.dribbling",
                    "curve": "$attack_skills.curve",
                    "freekick_accuracy": "$attack_skills.freekick_accuracy",
                    "long_passing": "$attack_skills.long_passing",
                    "ball_control": "$attack_skills.ball_control",
                    "long_shots": "$attack_skills.long_shots",
                    "positioning": "$attack_skills.positioning",
                    "vision": "$attack_skills.vision",
                    # Physical stats
                    "acceleration": "$physical_stats.acceleration",
                    "sprint_speed": "$physical_stats.sprint_speed",
                    "agility": "$physical_stats.agility",
                    "balance": "$physical_stats.balance",
                    "shot_power": "$physical_stats.shot_power",
                    "jumping": "$physical_stats.jumping",
                    "stamina": "$physical_stats.stamina",
                    "strength": "$physical_stats.strength",
                    "composure": "$physical_stats.composure",
                    # Defense stats
                    "standing_tackle": "$defense_stats.standing_tackle",
                    "sliding_tackle": "$defense_stats.sliding_tackle",
                    "interceptions": "$defense_stats.interceptions"
                }
            },
            {
                "$sort": {"overall_rating": -1}
            },
            {
                "$limit": 2000  # Giới hạn để tránh memory limit
            }
        ]
        
        data = list(player_col.aggregate(pipeline))
        
        if not data:
            st.warning(" Không tìm thấy dữ liệu cầu thủ trong database")
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Làm sạch dữ liệu
        df = df.dropna(subset=['name', 'overall_rating'])
        df = df.fillna(0)  # Điền 0 cho các giá trị NaN trong stats
        
        return df
        
    except Exception as e:
        st.error(f" Lỗi khi tải dữ liệu: {e}")
        return pd.DataFrame()
# ============= hàm tìm kiếm cầu thủ theo tên =============
def search_player_by_name(player_name):
    """Tìm cầu thủ theo tên với error handling"""
    db = init_connection()
    if db is None:
        return None
    
    collection = db.players
    
    try:
        result = collection.find_one(
            {"name": {"$regex": player_name, "$options": "i"}}
        )
        return result
    except Exception as e:
        st.error(f" Lỗi tìm kiếm cầu thủ: {e}")
        return None

def create_radar_chart(player_data, skills, player_name):
    """Tạo biểu đồ radar cho một cầu thủ với error handling"""
    try:
        # Chuẩn bị dữ liệu
        values = []
        labels = []
        
        for skill in skills:
            if skill in player_data and pd.notna(player_data[skill]):
                value = float(player_data[skill]) if player_data[skill] != 0 else 0
                values.append(value)
                labels.append(skill.replace('_', ' ').title())
        
        if not values:
            st.warning(" Không có dữ liệu để hiển thị cho cầu thủ này.")
            return
        
        # Đóng vòng tròn cho radar chart
        values += values[:1] 
        labels += labels[:1]
        
        # Tạo biểu đồ
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            name=player_name,
            line=dict(color='rgb(102, 126, 234)', width=3),
            fillcolor='rgba(102, 126, 234, 0.3)',
            marker=dict(size=8, color='rgb(102, 126, 234)')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(size=10),
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=11, color='#2d3748')
                )
            ),
            showlegend=True,
            title=dict(
                text=f" Radar Chart - {player_name}",
                x=0.5,
                font=dict(size=18, color='#2d3748')
            ),
            height=800,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f" Lỗi tạo radar chart: {e}")

def create_comparison_chart(player1_data, player2_data, skills, name1, name2):
    """Tạo biểu đồ so sánh hai cầu thủ với error handling"""
    try:
        values1, values2, labels = [], [], []
        
        for skill in skills:
            if skill in player1_data and skill in player2_data:
                if pd.notna(player1_data[skill]) and pd.notna(player2_data[skill]):
                    val1 = float(player1_data[skill]) if player1_data[skill] != 0 else 0
                    val2 = float(player2_data[skill]) if player2_data[skill] != 0 else 0
                    values1.append(val1)
                    values2.append(val2)
                    labels.append(skill.replace('_', ' ').title())
        
        if not values1 or not values2:
            st.warning(" Không có dữ liệu để so sánh giữa hai cầu thủ này.")
            return
        
        # Đóng vòng tròn
        values1 += values1[:1]
        values2 += values2[:1]
        labels += labels[:1]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values1,
            theta=labels,
            fill='toself',
            name=name1,
            line=dict(color='rgb(102, 126, 234)', width=3),
            fillcolor='rgba(102, 126, 234, 0.25)',
            marker=dict(size=6, color='rgb(102, 126, 234)')
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=values2,
            theta=labels,
            fill='toself',
            name=name2,
            line=dict(color='rgb(255, 99, 71)', width=3),
            fillcolor='rgba(255, 99, 71, 0.25)',
            marker=dict(size=6, color='rgb(255, 99, 71)')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(size=10),
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=11, color="#1b325a")
                )
            ),
            showlegend=True,
            title=dict(
                text=f" So sánh: {name1} vs {name2}",
                x=0.5,
                font=dict(size=18, color="#1b2d4e")
            ),
            height=800,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f" Lỗi tạo comparison chart: {e}")

def display_top_skills(player_data, selected_skills, num_skills=5):
    """Hiển thị top kỹ năng với styling tốt hơn"""
    try:
        skill_values = []
        for skill in selected_skills:
            if skill in player_data and pd.notna(player_data[skill]) and player_data[skill] > 0:
                skill_values.append((skill, float(player_data[skill])))
        
        if skill_values:
            skill_values.sort(key=lambda x: x[1], reverse=True)
            
            # Tạo container cho top skills
            st.markdown("""
            <div style="background: linear-gradient(145deg, #4facfe, #00f2fe); 
                       color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                <h3 style="color: white; margin-bottom: 1rem;"> Top 5 kỹ năng</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Sử dụng columns để hiển thị skills
            for i, (skill, value) in enumerate(skill_values[:num_skills], 1):
                skill_name = skill.replace('_', ' ').title()
                
                # Sử dụng st.info với emoji và formatting
                st.info(f" **{i}. {skill_name}:** {value:.1f}")
        else:
            st.error(" Không có dữ liệu kỹ năng để hiển thị")
            
    except Exception as e:
        st.error(f" Lỗi hiển thị top skills: {e}")

def display_skill_comparison_table(player1_data, player2_data, skills, name1, name2):
    """Tạo bảng so sánh chi tiết giữa hai cầu thủ"""
    try:
        comparison_data = []
        
        for skill in skills:
            if skill in player1_data and skill in player2_data:
                if pd.notna(player1_data[skill]) and pd.notna(player2_data[skill]):
                    val1 = float(player1_data[skill]) if player1_data[skill] != 0 else 0
                    val2 = float(player2_data[skill]) if player2_data[skill] != 0 else 0
                    diff = val1 - val2
                    
                    comparison_data.append({
                        'Kỹ năng': skill.replace('_', ' ').title(),
                        name1: val1,
                        name2: val2,
                        'Chênh lệch': f"{diff:+.1f}"
                    })
        
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True)
        else:
            st.warning(" Không có dữ liệu để so sánh")
            
    except Exception as e:
        st.error(f" Lỗi tạo bảng so sánh: {e}")

def main():
    """Main function với comprehensive error handling"""
    try:
        # Custom header
        st.markdown("""
        <div class="custom-header">
            <h1> FIFA Player Radar Chart</h1>
            <p>Phân tích thống kê cầu thủ chi tiết</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar cho tùy chọn
        st.sidebar.header(" Tùy chọn phân tích")
        
        # Load data với progress bar
        with st.spinner(' Đang tải dữ liệu từ MongoDB...'):
            df = load_data()
        
        if df.empty:
            st.error(" Không thể tải dữ liệu từ MongoDB.")
            st.info(" Các bước kiểm tra:")
            st.info("- Thông tin đăng nhập MongoDB Atlas chính xác")
            st.info("- Database 'fifa_database' và collection 'players' tồn tại")
            st.info("- IP address được whitelist trong MongoDB Atlas")
            st.info("- Kết nối internet ổn định")
            return
        
        
        
        # Kiểm tra dữ liệu có hợp lệ không
        if 'name' not in df.columns:
            st.error(" Dữ liệu không có trường 'name'")
            return
        
        # Chọn cầu thủ
        player_names = sorted(df['name'].unique().tolist())
        if not player_names:
            st.error(" Không tìm thấy tên cầu thủ trong dữ liệu")
            return
            
        selected_player = st.sidebar.selectbox("🏃‍♂️ Chọn cầu thủ:", player_names)
        
        # Chọn loại biểu đồ radar
        chart_type = st.sidebar.selectbox(
            " Chọn loại thống kê:",
            ["Tổng quan", "Tấn công", "Thể lực", "Phòng ngự", "Tùy chỉnh"]
        )
        
        # Lấy dữ liệu cầu thủ được chọn
        player_data_df = df[df['name'] == selected_player]
        if player_data_df.empty:
            st.error(f" Không tìm thấy dữ liệu cho cầu thủ {selected_player}")
            return
            
        player_data = player_data_df.iloc[0]
        
        # Định nghĩa các nhóm kỹ năng
        attack_skills = ['crossing', 'finishing', 'heading_accuracy', 'short_passing', 
                        'volleys', 'dribbling', 'curve', 'freekick_accuracy', 
                        'long_passing', 'ball_control', 'long_shots', 'positioning', 'vision']
        
        physical_skills = ['acceleration', 'sprint_speed', 'agility', 'balance', 
                          'shot_power', 'jumping', 'stamina', 'strength', 'composure']
        
        defense_skills = ['standing_tackle', 'sliding_tackle', 'interceptions']
        
        overview_skills = ['finishing', 'dribbling', 'short_passing', 'ball_control', 
                          'acceleration', 'agility', 'composure', 'positioning']
        
        # Chọn kỹ năng dựa trên loại biểu đồ
        if chart_type == "Tấn công":
            selected_skills = attack_skills
        elif chart_type == "Thể lực":
            selected_skills = physical_skills
        elif chart_type == "Phòng ngự":
            selected_skills = defense_skills
        elif chart_type == "Tổng quan":
            selected_skills = overview_skills
        else:  # Tùy chỉnh
            all_skills = attack_skills + physical_skills + defense_skills
            # Lọc các skills có trong dữ liệu
            available_skills = [skill for skill in all_skills if skill in df.columns]
            selected_skills = st.sidebar.multiselect(
                "Chọn kỹ năng hiển thị:",
                available_skills,
                default=[skill for skill in overview_skills if skill in available_skills]
            )
        
        # Layout chính
        col1, col2 = st.columns([2, 1])
        
        with col1:
            create_radar_chart(player_data, selected_skills, selected_player)
        
        with col2:
            # Thông tin cầu thủ
            overall_rating = player_data.get('overall_rating', 'N/A')
            positions = player_data.get('positions', 'N/A')
            
            st.markdown(f"""
            <div class="player-info">
                <h3> Thông tin cầu thủ</h3>
                <p><strong>Tên:</strong> {player_data['name']}</p>
                <p><strong>Overall Rating:</strong> {overall_rating}</p>
                <p><strong>Vị trí:</strong> {positions}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Hiển thị top kỹ năng với function mới
            display_top_skills(player_data, selected_skills)
            
            # Stats info
            st.markdown(f"""
            <div class="stats-info">
                 Đang hiển thị {len(selected_skills)} kỹ năng<br>
                 Loại: {chart_type}
            </div>
            """, unsafe_allow_html=True)
            

        
        # So sánh với cầu thủ khác
        st.markdown("###  So sánh cầu thủ")
        other_players = [p for p in player_names if p != selected_player]
        if other_players:
            compare_player = st.selectbox("Chọn cầu thủ để so sánh:", other_players)
            
            if compare_player:
                compare_data_df = df[df['name'] == compare_player]
                if not compare_data_df.empty:
                    compare_data = compare_data_df.iloc[0]
                    
                    # Tạo tabs cho comparison
                    tab1, tab2 = st.tabs([" Radar Chart", "Bảng so sánh"])
                    
                    with tab1:
                        create_comparison_chart(player_data, compare_data, selected_skills, 
                                              selected_player, compare_player)
                    
                    with tab2:
                        display_skill_comparison_table(player_data, compare_data, selected_skills,
                                                     selected_player, compare_player)
                else:
                    st.error(f" Không tìm thấy dữ liệu cho cầu thủ {compare_player}")
        else:
            st.info("Không có cầu thủ khác để so sánh")
    
    except Exception as e:
        st.error(f" Lỗi trong main function: {str(e)}")
        st.info("Vui lòng:")
        st.info("- Kiểm tra kết nối internet")
        st.info("- Kiểm tra thông tin đăng nhập MongoDB Atlas")
        st.info("- Kiểm tra cấu trúc database và collection")
        st.info("- Refresh lại trang và thử lại")

if __name__ == "__main__":
    main()