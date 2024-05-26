import streamlit as st
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS
import plotly.express as px
import matplotlib.pyplot as plt
import itertools
from collections import Counter

@st.cache_resource
def load_data():
    # Load data here, adjust 'task_02_result.csv' to your actual data file path
    df = pd.read_csv('task_02_result.csv')
    return df

def plot_target_groups_by_category(data):
    if data is not None:
        # Get unique categories
        categories = data['Categories'].unique()

        for category in categories:
            # Filter data for the selected category
            filtered_data = data[data['Categories'] == category]

            # Calculate the frequency of each target group in the selected category
            target_group_counts = filtered_data['Target Group'].value_counts().reset_index()
            target_group_counts.columns = ['Target Group', 'Count']

            # Create an interactive bar chart using Plotly
            fig = px.bar(target_group_counts, 
                         x='Count', 
                         y='Target Group', 
                         orientation='h',
                         title=f'Frequency of Target Groups in {category}', 
                         labels={'Count': 'Frequency', 'Target Group': 'Target Groups'},
                         template='plotly_white',
                         color='Target Group',  # Color by Target Group
                         color_discrete_sequence=px.colors.qualitative.Set3  # Use a qualitative color set
                         )


            # Display the interactive bar chart
            st.plotly_chart(fig)


def plot_target_group_word_cloud(data):
    if data is not None:
        # Filter data for religious and political offensive categories
        religious_offensive_data = data[data['Categories'] == 'religious offensive']
        political_offensive_data = data[data['Categories'] == 'political offensive']

        # Concatenate all target group entries into one large string
        text_religious = ' '.join(group for group in religious_offensive_data['Target Group'] if group != 'no-target')
        text_political = ' '.join(group for group in political_offensive_data['Target Group'] if group != 'no-target')
        
        # Generate word clouds
        wordcloud_religious = WordCloud(width=800, height=400, background_color='white').generate(text_religious)
        wordcloud_political = WordCloud(width=800, height=400, background_color='white').generate(text_political)

        # Display the word clouds
        st.write("Word Cloud for Target Groups in Religious Offensive Category")
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud_religious, interpolation='bilinear')
        plt.axis("off")
        st.pyplot(plt)

        st.write("Word Cloud for Target Groups in Political Offensive Category")
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud_political, interpolation='bilinear')
        plt.axis("off")
        st.pyplot(plt)

def plot_pie_chart_with_table(data):
    categories = data['Categories'].unique()
    selected_category = st.selectbox('Select a category:', categories)
    
    # Filter the data for the selected category
    filtered_data = data[data['Categories'] == selected_category]
    
    # Count occurrences
    target_counts = filtered_data['Target Group'].value_counts()
    total_counts = target_counts.sum()
    
    # Calculate percentages
    target_percentages = (target_counts / total_counts * 100).round(1).astype(str) + '%'
    
    # Create the pie chart 
    fig, ax = plt.subplots()
    ax.pie(target_counts, labels=target_counts.index, autopct='%1.1f%%', startangle=360)
    ax.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle.
    plt.title(f'Target Group Distribution in {selected_category}')
    st.pyplot(fig)
    
    # Create a DataFrame for the table
    table_data = pd.DataFrame({
        'Target Group': target_counts.index,
        'Count': target_counts.values,
        'Percentage': target_percentages.values
    })
    
    # Display the table
    st.write("Detailed counts and percentages:")
    st.table(table_data)

def plot_top_offensive_words(data, category, top_n=20):
    # Filter data for the selected category
    filtered_data = data[data['Categories'] == category]
    
    # Count occurrences of offensive words in the selected category
    offensive_word_counts = filtered_data['Offensive Words'].value_counts().head(top_n)
    
    # Plotting the top N offensive words
    plt.figure(figsize=(10, 6))
    sns.barplot(x=offensive_word_counts.values, y=offensive_word_counts.index, palette='viridis')
    plt.title(f'Top {top_n} Offensive Words in {category}')
    plt.xlabel('Frequency')
    plt.ylabel('Offensive Words')
    plt.tight_layout()
    st.pyplot(plt)

def get_most_frequent_offensive_words(data):
    # Get unique categories
    categories = data['Categories'].unique()
    
    # Dictionary to store the most frequent offensive words for each category
    most_frequent_words = {}

    # Calculate the most frequent offensive words for each category
    for category in categories:
        filtered_data = data[data['Categories'] == category]
        offensive_word_counts = filtered_data['Offensive Words'].value_counts()
        most_frequent_words[category] = offensive_word_counts.head(10)  # Get top 10 most frequent words
    
    return most_frequent_words

def display_most_frequent_offensive_words(most_frequent_words):
    # Display the most frequent offensive words for each category
    for category, words in most_frequent_words.items():
        # Filter out "no-offensive"
        words = words[words.index != 'no-offensive']
        st.write(f"Most frequent offensive words in '{category}' category:")
        st.table(words.reset_index().rename(columns={'index': 'Offensive Word', 'Offensive Words': 'Count'}))

def generate_word_cloud(data, category, stopwords):
    # Filter data for the selected category
    filtered_data = data[data['Categories'] == category]
    
    # Combine all offensive words into a single string
    text = ' '.join(filtered_data['Offensive Words'].dropna())
    
    # Generate word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords).generate(text)
    
    # Display the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Word Cloud for Offensive Words in {category}')
    st.pyplot(plt)

def plot_most_common_offensive_words_by_category(data, top_n=20):
    categories = data['Categories'].unique()
    for category in categories:
        st.subheader(f"Category: {category}")

        # Filter data for the selected category
        filtered_data = data[data['Categories'] == category]
        
        # Extract and flatten offensive words
        offensive_words = filtered_data['Offensive Words'].apply(lambda x: x.split(', '))
        flattened_words = list(itertools.chain(*offensive_words))
        flattened_words = [word for word in flattened_words if word != 'no-offensive']
        
        # Count the frequency of each word
        word_counts = Counter(flattened_words)
        most_common_words = word_counts.most_common(top_n)
        
        if most_common_words:
            # Separate the words and their counts
            words, counts = zip(*most_common_words)
            
            # Plot the most common offensive words
            fig, ax = plt.subplots()
            ax.barh(words, counts, color='salmon')
            ax.set_title(f'Most Common Offensive Words in {category}')
            ax.set_xlabel('Count')
            ax.set_ylabel('Offensive Words')
            ax.invert_yaxis()
            #st.pyplot(fig)
            
            # Display the most common offensive words in a table
            st.write(f"Table of Most Common Offensive Words in {category}")
            common_words_df = pd.DataFrame(most_common_words, columns=['Offensive Word', 'Count'])
            st.table(common_words_df)
        else:
            st.write("No offensive words found in this category.")


def main():
    st.title('Target Group and Offensive Word Analysis')

    # Load data
    data = load_data()
    st.header("Data Overview")
    st.dataframe(data)
    
    st.header("Target Group Identification")
    with st.expander("Click here to see bar chart for categories"):    
        plot_target_groups_by_category(data)

    with st.expander("Click here to see word cloud by each category"):
        plot_target_group_word_cloud(data)

    st.header('Analysis of Target Groups by Category')
    plot_pie_chart_with_table(data)

    # st.header('Most Frequent Offensive Words by Category')
    # most_frequent_words = get_most_frequent_offensive_words(data)
    # display_most_frequent_offensive_words(most_frequent_words)
    
    st.header('Top Offensive Words by Category')
    # Dropdown menu for user to select a category
    categories = data['Categories'].unique()
    selected_category = st.selectbox('Select a category to view top offensive words:', categories, key='top_words_category_select')
    top_n = st.slider('Select number of top words to display:', 1, 50, 20)
    if selected_category:
        plot_top_offensive_words(data, selected_category, top_n)

    st.header('Word Cloud of Offensive Words by Category')
    stopwords = set(STOPWORDS)
    # Add specific words to ignore
    stopwords.update(['Offensive', 'no-offensive'])  # Replace with actual words to ignore

    selected_wc_category = st.selectbox('Select a category to view word cloud:', categories, key='wc_category_select')
    if selected_wc_category:
        generate_word_cloud(data, selected_wc_category, stopwords)

    # 1. Category Distribution
    st.header("Distribution of Offensive Categories")
    category_counts = data['Categories'].value_counts()

    fig, ax = plt.subplots()
    category_counts.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title('Distribution of Offensive Categories')
    ax.set_xlabel('Category')
    ax.set_ylabel('Count')
    ax.set_xticklabels(category_counts.index, rotation=45)
    st.pyplot(fig)

    st.write(category_counts)

    # 2. Target Group Analysis
    st.header("Distribution of Target Groups")
    target_group_counts = data['Target Group'].value_counts()

    fig, ax = plt.subplots()
    target_group_counts.plot(kind='bar', color='lightgreen', ax=ax)
    ax.set_title('Distribution of Target Groups')
    ax.set_xlabel('Target Group')
    ax.set_ylabel('Count')
    ax.set_xticklabels(target_group_counts.index, rotation=45)
    st.pyplot(fig)

    st.write(target_group_counts)

    # 3. Offensive Words Analysis
    st.header("Most Common Offensive Words")
    offensive_words = data['Offensive Words'].apply(lambda x: x.split(', '))
    flattened_words = list(itertools.chain(*offensive_words))
    flattened_words = [word for word in flattened_words if word != 'no-offensive']

    word_counts = Counter(flattened_words)
    most_common_words = word_counts.most_common(20)

    words, counts = zip(*most_common_words)

    fig, ax = plt.subplots()
    ax.barh(words, counts, color='salmon')
    ax.set_title('Most Common Offensive Words')
    ax.set_xlabel('Count')
    ax.set_ylabel('Offensive Words')
    ax.invert_yaxis()
    st.pyplot(fig)

    st.write(pd.DataFrame(most_common_words, columns=['Offensive Word', 'Count']))

    # 5. Sentence Length Analysis
    st.header("Distribution of Sentence Lengths")
    data['Sentence Length'] = data['Sentence'].apply(len)

    fig, ax = plt.subplots()
    data['Sentence Length'].plot(kind='hist', bins=30, color='purple', edgecolor='black', ax=ax)
    ax.set_title('Distribution of Sentence Lengths')
    ax.set_xlabel('Sentence Length')
    ax.set_ylabel('Frequency')
    st.pyplot(fig)

    sentence_length_stats = data['Sentence Length'].describe()
    st.write(sentence_length_stats)

    # Identifying the most offensive sentences based on the number of offensive words
    data['Offensive Word Count'] = data['Offensive Words'].apply(lambda x: len(x.split(', ')))
    most_offensive_sentences = data.sort_values(by='Offensive Word Count', ascending=False).head(10)

    st.header("Most Offensive Sentences")
    st.write(most_offensive_sentences[['Sentence', 'Categories', 'Target Group', 'Offensive Words', 'Offensive Word Count']])


    st.header("Most Common Offensive Words by Category")
    plot_most_common_offensive_words_by_category(data)

#
if __name__ == "__main__":
    main()