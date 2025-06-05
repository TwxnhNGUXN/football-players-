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

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="Data Never Lies",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS cho styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .stTab {
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== MongoDB CONNECTION  ==========
@st.cache_resource
def init_connection():
    username = "lilduckhoa102"
    password = "5pSgoZXMuomY8w8r"
    cluster = "football-player-db.vk7ebjz.mongodb.net"
    encoded_password = quote_plus(password)
    uri = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?retryWrites=true&w=majority"

    try:
        client = MongoClient(uri, tlsCAFile=certifi.where())
        client.admin.command("ping")
        db = client['fifa_database']
        return db
    except Exception as e:
        st.error(f" Lỗi kết nối MongoDB: {e}")
        return None

# ========== hàm lấy dữ liệu ==========
@st.cache_data 
def get_gk_stats_15():
    db = init_connection()
    if db is None:
        return pd.DataFrame()

    gk_col = db['goalkeeper_stats']
    
    pipeline = [
        {
            "$match": {
                "90s": { "$gte": 15 },
                "PSxG+/-": { "$exists": True },
                "Stp%": { "$exists": True },
                "#OPA/90": { "$exists": True }
            }
        },
        {
            "$addFields": {
                "performance_score": {
                    "$add": [
                        { "$multiply": ["$PSxG+/-", -10] },
                        { "$divide": ["$Stp%", 10] },
                        { "$divide": ["$#OPA/90", 5] },
                        { "$divide": ["$Cmp%", 20] }
                    ]
                }
            }
        },
        {
            "$project": {
                "Player": 1,
                "Squad": 1,
                "Age": 1,
                "90s": 1,
                "PSxG+/-": 1,
                "Stp%": 1,
                "#OPA/90": 1,
                "Cmp%": 1,
                "performance_score": { "$round": ["$performance_score", 2] },
                "overall_rating": {
                    "$switch": {
                        "branches": [
                            { "case": { "$gte": ["$performance_score", 15] }, "then": "Thủ môn tốt có khả năng phản xạ nhanh" },
                            { "case": { "$gte": ["$performance_score", 10] }, "then": "Thủ môn khá " },
                            { "case": { "$gte": ["$performance_score", 5] }, "then": "Thủ môn trung bình" },
                            { "case": { "$lt": ["$performance_score", 5] }, "then": "Cần cải thiện" }
                        ],
                        "default": "Chưa đủ dữ liệu"
                    }
                }
            }
        },
        { "$sort": { "performance_score": -1 } },
        { "$limit": 20 }
    ]

    result = list(gk_col.aggregate(pipeline))
    return result if result else {}




@st.cache_data 
def get_gk_pass_the_ball():

    db = init_connection()
    if db is None:
        return pd.DataFrame()
    
    gk_col = db['goalkeeper_stats']
    
    pipeline = [
        {
            "$match": {
                "90s": { "$gte": 5 },
                "Cmp%": { "$exists": True },
                "Launch%": { "$exists": True }
            }
        },
        {
            "$project": {
                "Player": 1,
                "Squad": 1,
                "Cmp%": 1,
                "Launch%": 1,
                "AvgLen": 1,
                "distribution_style": {
                    "$switch": {
                        "branches": [
                            { 
                                "case": {
                                    "$and": [
                                        { "$gte": ["$Cmp%", 40] },
                                        { "$lte": ["$Launch%", 20] }
                                    ]
                                },
                                "then": "Chơi bóng ngắn thủ môn chơi chân tốt - Phát triển bóng từ sân nhà, kiểm soát bóng"
                            },
                            {
                                "case": {
                                    "$and": [
                                        { "$gte": ["$Launch%",20 ] },
                                        { "$gte": ["$AvgLen", 30] }
                                    ]
                                },
                                "then": "Chuyền dài nhiều nhưng thiếu sự ổn định chính xác"
                            },
                            {
                                "case": {
                                    "$and": [
                                        { "$gte": ["$Cmp%", 50] },
                                        { "$and": [
                                            { "$gte": ["$Launch%", 30] },
                                            { "$lte": ["$Launch%", 15] },
                                            { "$lt": ["$AvgLen", 30] }
                                        ]}
                                    ]
                                },
                                "then": "Phân phối linh hoạt - Biết khi nào chơi ngắn/dài"
                            }
                        ],
                        "default": "Thủ môn chơi chân không tốt "
                    }
                }
            }
        }
    ]
    
    result = list(gk_col.aggregate(pipeline))
    return pd.DataFrame(result)



@st.cache_data
def get_gk_sweeper():
    db = init_connection()
    if db is None:
        return pd.DataFrame()

    gk_col = db['goalkeeper_stats']

    pipeline = [
        {
            "$match": {
                "90s": {"$gte": 5},
                "#OPA/90": {"$exists": True}
            }
        },
        {
            "$project": {
                "Player": 1,
                "Squad": 1,
                "#OPA/90": 1,
                "AvgDist": 1,
                "sweeper_style": {
                    "$switch": {
                        "branches": [
                            {
                                "case": {"$gte": ["$#OPA/90",2]},
                                "then": "Thủ môn quét có xu hướng rời khỏi khung thành"
                            },
                            {
                                "case": {
                                    "$and": [
                                        {"$lt": ["$#OPA/90", 2]},
                                        {"$lt": ["$AvgDist", 15]}
                                    ]
                                },
                                "then": "Thủ môn truyền thống"
                            }
                        ],
                        "default": "Cần đánh giá thêm"
                    }
                }
            }
        },
        {
            "$sort": {"#OPA/90": -1}
        }
    ]

    result = list(gk_col.aggregate(pipeline))
    return pd.DataFrame(result)

#df = pd.DataFrame(get_gk_sweeper())
#st.dataframe(df, use_container_width=True)



# ========== hàm vẽ scatter plot ==========
def create_gk_scatter_plots(gk_data, pass_data):
    """
    Tạo các biểu đồ phân tán cho dữ liệu thủ môn
    """
    if not gk_data:
        st.warning("Không có dữ liệu để hiển thị")
        return
    
    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(gk_data)
    
    # Tạo màu sắc theo rating
    color_map = {
        'Thủ môn xuất sắc': "#b41fb2",
        'Thủ môn tốt': "#53a02c",
        'Thủ môn trung bình': '#ff7f0e',
        'Cần cải thiện': '#d62728'
    }
    
    df['color'] = df['overall_rating'].map(color_map)
    
    st.title(" Phân Tích Hiệu Suất Thủ Môn")
    st.markdown("---")
    
    # Sidebar cho tùy chọn
    st.sidebar.header(" Tùy Chọn Biểu Đồ")
    
    # Chọn loại biểu đồ
    chart_type = st.sidebar.selectbox(
        "Chọn loại biểu đồ:",
        ["Performance Score vs PSxG+/-",  
         "Age vs Performance", 
         "Footwork",
         "Sweeper Keeper"]
    )
    
    # Chọn rating để lọc
    selected_ratings = st.sidebar.multiselect(
        "Lọc theo xếp hạng:",
        options=df['overall_rating'].unique(),
        default=df['overall_rating'].unique(),
    )
    
    # Lọc dữ liệu
    filtered_df = df[df['overall_rating'].isin(selected_ratings)]
    
    if chart_type == "Performance Score vs PSxG+/-":
        # Biểu đồ 1: Performance Score vs PSxG+/-
        fig = px.scatter(
            filtered_df, 
            x='PSxG+/-', 
            y='performance_score',
            color='overall_rating',
            size='90s',
            hover_data=['Player', 'Squad', 'Age', 'Stp%'],
            title=" Performance Score vs PSxG+/- (Post-Shot Expected Goals)",
            labels={
                'PSxG+/-': 'PSxG+/- (Âm = Tốt)',
                'performance_score': 'Điểm Hiệu Suất',
                'overall_rating': 'Xếp Hạng'
            },
            color_discrete_map=color_map
        )
        
        # Thêm đường tham chiếu
        fig.add_hline(y=10, line_dash="dash", line_color="gray", 
                     annotation_text="Ngưỡng Thủ Môn Tốt")
        fig.add_vline(x=0, line_dash="dash", line_color="gray",
                     annotation_text="PSxG+/- = 0")
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        ** Chú thích:**
        - **PSxG+/-**: Giá trị âm = thủ môn cản phá tốt hơn dự kiến
        - **Performance Score**: Điểm tổng hợp từ nhiều chỉ số
        - **Bong bóng**: Số trận đấu (90s=1 trận thi đấu)
        """)
    
    elif chart_type == "Age vs Performance":
        # Biểu đồ 2: Age vs Performance
        fig = px.scatter(
            filtered_df,
            x='Age',
            y='performance_score',
            color='overall_rating',
            size='90s',
            hover_data=['Player', 'Squad', 'PSxG+/-', 'Stp%'],
            title=" Tuổi vs Hiệu Suất",
            labels={
                'Age': 'Tuổi',
                'performance_score': 'Điểm Hiệu Suất',
                'overall_rating': 'Xếp Hạng'
            },
            color_discrete_map=color_map
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Footwork":
        # Biểu đồ 3: Pass Distribution Analysis
        st.subheader(" Khả năng chuyền bóng của thủ môn ")
        
        if not pass_data.empty:
            # Tạo màu sắc cho từng phong cách
            pass_color_map = {
                'Chơi bóng ngắn thủ môn chơi chân tốt - Phát triển bóng từ sân nhà, kiểm soát bóng': '#2E8B57',
                'Chuyền dài nhiều nhưng thiếu sự ổn định chính xác': '#FF6347',
                'Phân phối linh hoạt - Biết khi nào chơi ngắn/dài': '#4169E1',
                'Thủ môn chơi chân không tốt ': '#DC143C'
            }
            
            # Biểu đồ phân tán: Completion% vs Launch%
            fig1 = px.scatter(
                pass_data,
                x='Launch%',
                y='Cmp%',
                color='distribution_style',
                size='AvgLen',
                hover_data=['Player', 'Squad'],
                title=" Tỷ lệ Chuyền dài vs Độ chính xác",
                labels={
                    'Launch%': 'Tỷ lệ Chuyền dài (%)',
                    'Cmp%': 'Độ chính xác chuyền (%)',
                    'distribution_style': 'Khả năng chuyền bóng'
                },
                color_discrete_map=pass_color_map
            )
            
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown("""
            ** Chú thích:**
            - **Cmp%**: tỷ lệ chuyền thành công càng cao càng tốt
            - **Launch%**: tỷ lệ chuyền dài càng cao nghĩa là phát bóng nhiều
            - **AvgLen**: độ dài trung bình của các đường bóng 
            """)
            
            # Hiển thị top performers mỗi category
            st.subheader(" Top Performers theo từng phong cách")
            
            for style in pass_data['distribution_style'].unique():
                with st.expander(f" {style}"):
                    style_df = pass_data[pass_data['distribution_style'] == style]
                    style_df_sorted = style_df.sort_values('Cmp%', ascending=False).head(5)
                    st.dataframe(
                        style_df_sorted[['Player', 'Squad', 'Cmp%', 'Launch%', 'AvgLen']],
                        use_container_width=True
                    )
        
            
    elif chart_type == "Sweeper Keeper":
        # Biểu đồ 4: Sweeper Keeper Analysis
        st.subheader(" Phân Tích Thủ Môn Quét")
        
        # Gọi function và nhận DataFrame
        sweeper_df = get_gk_sweeper()  # Function này trả về DataFrame
        
       
        
        # Kiểm tra DataFrame có dữ liệu không (an toàn hơn)
        if sweeper_df is not None and hasattr(sweeper_df, 'empty') and not sweeper_df.empty:
            
            # Tạo color map cho sweeper style
            sweeper_color_map = {
                'Thủ môn quét có xu hướng rời khỏi khung thành': '#FF4500',
                'Thủ môn truyền thống': '#32CD32',
                'Cần đánh giá thêm': '#FFA500'
            }
            
            # Tạo biểu đồ scatter
            fig3 = px.scatter(
                sweeper_df,
                x='#OPA/90',
                y='AvgDist',
                color='sweeper_style',
                hover_data=['Player', 'Squad'],
                title="🏃‍♂️ Số lần can thiệp trung bình mỗi trận vs Khoảng cách trung bình",
                labels={
                    '#OPA/90': 'Số lần can thiệp trung bình mỗi trận',
                    'AvgDist': 'Khoảng cách trung bình (m)',
                    'sweeper_style': 'Phong cách thủ môn quét'
                },
                color_discrete_map=sweeper_color_map
            )
            
            # Thêm đường tham chiếu
            fig3.add_hline(y=15, line_dash="dash", line_color="gray", 
                          annotation_text="Ngưỡng 15m")
            fig3.add_vline(x=2, line_dash="dash", line_color="gray",
                          annotation_text="2 lần/trận")
            
            st.plotly_chart(fig3, use_container_width=True)
            
            st.markdown("""
            ** Chú thích:**
            - **#OPA/90**: Số lần can thiệp bên ngoài vòng cấm địa trung bình mỗi trận
            - **AvgDist**: Khoảng cách trung bình từ khung thành đến vi trí can thiệp
            
            """)
            
            # Hiển thị top performers theo từng phong cách
            st.subheader(" Top Performers theo phong cách thủ môn quét")
            
            for style in sweeper_df['sweeper_style'].unique():
                with st.expander(f" {style}"):
                    style_df = sweeper_df[sweeper_df['sweeper_style'] == style]
                    style_df_sorted = style_df.sort_values('#OPA/90', ascending=False).head(5)
                    st.dataframe(
                        style_df_sorted[['Player', 'Squad', '#OPA/90', 'AvgDist']],
                        use_container_width=True
                    )
            
            # Hiển thị toàn bộ dữ liệu
            st.subheader(" Dữ liệu đầy đủ")
            st.dataframe(sweeper_df, use_container_width=True)
            
        else:
            st.warning(" Không có dữ liệu cho phân tích thủ môn quét")
            st.info("Vui lòng kiểm tra kết nối database và dữ liệu")
            if sweeper_df is not None:
                st.write(f"Debug: DataFrame shape = {sweeper_df.shape}")
                st.write(f"Debug: DataFrame columns = {list(sweeper_df.columns)}")
            else:
                st.error("sweeper_df is None - Kiểm tra function get_gk_sweeper()")


    
    
    # Format lại DataFrame để hiển thị đẹp hơn
    display_df = filtered_df.copy()
    display_df = display_df.round(2)
    
    st.dataframe(
        display_df[['Player', 'Squad', 'Age', '90s', 'PSxG+/-', 'Stp%', 
                   '#OPA/90', 'Cmp%', 'performance_score', 'overall_rating']],
        use_container_width=True
    )


#  function gọi dữ liệu 
def main():
    # gọi TẤT CẢ dữ liệu 
    gk_data = get_gk_stats_15()
    pass_data = get_gk_pass_the_ball()  #  tránh gọi lại trong tab Footwork
    
    # Hiển thị thông báo kết nối 1 lần duy nhất
    if 'connection_shown' not in st.session_state:
        st.success("Kết nối MongoDB thành công!")
        st.session_state.connection_shown = True
    
    #  2 dataset tạo biểu đồ 
    create_gk_scatter_plots(gk_data, pass_data)
    
    
    
    
    st.markdown("- Với sự phát triển của bóng đá hiện đại, vai trò của thủ môn đã trở nên đa dạng hơn bao giờ hết. Từ việc cản phá những cú sút nguy hiểm đến khả năng phát động tấn công từ sân nhà, thủ môn ngày nay không chỉ là người bảo vệ khung thành mà còn là một phần quan trọng trong lối chơi tổng thể của đội bóng.")
    st.markdown("- Bằng cách phân tích các chỉ số như PSxG+/- (Post-Shot Expected Goals), Stp% (Save Percentage) và #OPA/90 (Opportunities Prevented per 90 minutes), chúng ta có thể đánh giá hiệu suất của thủ môn một cách toàn diện. Những thủ môn xuất sắc không chỉ có khả năng cản phá tốt mà còn biết cách phát động tấn công hiệu quả, giúp đội bóng kiểm soát trận đấu tốt hơn.") 
    st.markdown("- Việc phân tích khả năng chuyền bóng và phong cách chơi của thủ môn cũng giúp chúng ta hiểu rõ hơn về vai trò của họ trong việc xây dựng lối chơi. Thủ môn không chỉ là người đứng sau khung thành mà còn là người khởi xướng các pha tấn công, tạo ra sự khác biệt trong trận đấu.")
    st.markdown("- Phân tích cho thấy được tầm quan trọng của 1 thủ môn biết chơi chân giúp kiểm soát thế trận một cách tốt hơn.")
    st.markdown("- Ngoài ra việc phân tích có thể giúp đội bóng trong việc lựa chọn cầu thủ scouting và chuyển nhượng, tìm ra nhân sự phù hợp với chiến thuật.")


if __name__ == "__main__":
    main()