import streamlit as st
import requests
import base64
import pdfplumber
from memorystore import MemoryStore
from notifications import notifier
from model_handlers import model_manager

st.set_page_config(page_title='Meu Assistente Pessoal', layout='wide')
memory_store = MemoryStore()
st.title('Assistente Pessoal')

if 'last_question' not in st.session_state:
    st.session_state.last_question = None
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = None
if 'current_provider' not in st.session_state:
    st.session_state.current_provider = 'Local'
if 'current_model' not in st.session_state:
    st.session_state.current_model = 'Ollama'

with st.sidebar:
    st.header('⚙️ Configurações')
    st.markdown('### 🤖 Modelo de IA')
    
    # Seletor de Provedor
    providers = model_manager.get_providers()
    st.session_state.current_provider = st.selectbox(
        '🌐 Provedor:',
        options=providers,
        index=providers.index(st.session_state.current_provider) if st.session_state.current_provider in providers else 0,
        key='provider_selector'
    )
    
    # Seletor de Modelo (dinâmico baseado no provedor)
    modelos = model_manager.get_models(st.session_state.current_provider)
    st.session_state.current_model = st.selectbox(
        '🤖 Modelo:',
        options=modelos,
        index=modelos.index(st.session_state.current_model) if st.session_state.current_model in modelos else 0,
        key='model_selector'
    )
    
    # Mostrar informações do provedor selecionado
    if st.session_state.current_provider == 'Local':
        st.caption('📍 Local (rápido, sem custos)')
    elif st.session_state.current_provider == 'OpenAI':
        st.caption('☁️ OpenAI (poderoso, com custos)')
    elif st.session_state.current_provider == 'Google':
        st.caption('☁️ Google Gemini (avançado, com custos)')
    elif st.session_state.current_provider == 'Anthropic':
        st.caption('☁️ Anthropic Claude (inteligente, com custos)')
    
    st.divider()
    st.header('Memoria')
    tab1, tab2, tab3 = st.tabs(['Notas', 'Tarefas', 'Config'])
    
    with tab1:
        st.subheader('Salvar Nota')
        if st.session_state.last_question and st.session_state.last_answer:
            st.info('Q: ' + st.session_state.last_question[:100])
            st.info('R: ' + st.session_state.last_answer[:100])
            
            col1, col2 = st.columns(2)
            with col1:
                tags_input = st.text_input('Tags (separadas por virgula):')
            with col2:
                source_input = st.text_input('Fonte:', value='assistente')
            
            if st.button('💾 Salvar Nota'):
                tags = [t.strip() for t in tags_input.split(',') if t.strip()] or ['nota']
                memory_store.add_note(
                    text=f'{st.session_state.last_question[:50]}... → {st.session_state.last_answer[:50]}...',
                    tags=tags,
                    source=source_input or 'assistente',
                    question=st.session_state.last_question,
                    answer=st.session_state.last_answer
                )
                st.success('✅ Nota salva!')
                st.rerun()
        else:
            st.warning('Faça uma pergunta e receba uma resposta primeiro!')
        
        st.divider()
        st.subheader('Minhas Notas')
        notas = memory_store.get_notes()
        
        if notas:
            for i, nota in enumerate(notas):
                with st.expander(f"📝 {nota.get('text', '')[:60]}..."):
                    st.write(f"**Pergunta:** {nota.get('question', '')}")
                    st.write(f"**Resposta:** {nota.get('answer', '')}")
                    st.write(f"**Tags:** {', '.join(nota.get('tags', []))}")
                    st.write(f"**Fonte:** {nota.get('source', '')}")
                    
                    col_delete = st.columns([1])[0]
                    with col_delete:
                        if st.button('🗑️ Deletar', key=f'delete_note_{i}'):
                            memory_store.delete_note(i)
                            st.success('Nota deletada!')
                            st.rerun()
        else:
            st.info('Nenhuma nota salva ainda')
    
    with tab2:
        st.subheader('Nova Tarefa')
        tarefa = st.text_input('Descricao:')
        
        col1, col2 = st.columns(2)
        with col1:
            email_alert = st.checkbox('Email')
        with col2:
            telegram_alert = st.checkbox('Telegram')
        
        col3, col4 = st.columns(2)
        with col3:
            st.write('Horario do alerta:')
            hora_alerta = st.selectbox('Hora:', range(0, 24), key='hora_select')
        with col4:
            st.write(' ')
            minuto_alerta = st.selectbox('Minuto:', range(0, 60, 5), key='minuto_select')
        
        hora_formatada = f'{hora_alerta:02d}:{minuto_alerta:02d}'
        st.caption(f'Alerta agendado para: {hora_formatada}')
        
        if st.button('Adicionar Tarefa'):
            if tarefa.strip():
                alert_type = 'email' if email_alert else ('telegram' if telegram_alert else None)
                memory_store.add_task(tarefa, alert_enabled=bool(alert_type), alert_time=hora_formatada, alert_type=alert_type)
                st.success(f'Tarefa adicionada! Alerta: {alert_type or "Nenhum"} às {hora_formatada}')
                st.rerun()
            else:
                st.warning('Digite uma tarefa!')
        
        st.divider()
        st.subheader('Tarefas Pendentes')
        tarefas = memory_store.get_tasks()
        pendentes = [t for t in tarefas if not t.get('done')]
        
        if pendentes:
            for i, t in enumerate(tarefas):
                if not t.get('done'):
                    col_task, col_btn = st.columns([4, 1])
                    with col_task:
                        hora = t.get('alert_time', '--:--')
                        st.write(f'* {t["task"]} | {hora} ({t.get("alert_type", "nenhum")})')
                    with col_btn:
                        if st.button('OK', key=f'done_{i}'):
                            memory_store.mark_task_done(i)
                            st.rerun()
        else:
            st.info('Nenhuma tarefa pendente')
        
        st.divider()
        st.subheader('Concluidas')
        concluidas = [t for t in tarefas if t.get('done')]
        if concluidas:
            for t in concluidas:
                st.write(f'✓ {t["task"]}')
            
            if st.button('Limpar Concluidas'):
                memory_store.clear_completed_tasks()
                st.rerun()
        else:
            st.info('Nenhuma tarefa concluida')
    
    with tab3:
        st.subheader('Buscar Notas')
        busca_termo = st.text_input('Pesquisar notas:', placeholder='Digite palavras-chave...')
        if busca_termo:
            resultados = memory_store.search_notes(busca_termo, limit=5)
            if resultados:
                st.success(f'Encontradas {len(resultados)} nota(s)')
                for nota in resultados:
                    with st.expander(f"📌 {nota.get('text', '')[:60]}..."):
                        st.write(f"**P:** {nota.get('question', '')}")
                        st.write(f"**R:** {nota.get('answer', '')}")
            else:
                st.info('Nenhuma nota encontrada com esses termos')
        
        st.divider()
        st.subheader('Testes')
        if st.button('Teste Telegram'):
            resultado = notifier.send_telegram_alert('Teste!', 'Teste')
            if resultado['success']:
                st.success(resultado['message'])
            else:
                st.error(resultado['message'])

st.header('Chat')
user_input = st.text_area('Pergunta:', height=100)

# Informações sobre modelos com visão
with st.expander('ℹ️ Modelos com Suporte a Imagem/Vídeo/Áudio'):
    st.markdown("""
    ### 🎥 Modelos com Visão Avançada:
    - **GPT-4o (Multimodal)** ⭐ - Melhor: Imagens, vídeos, áudios
    - **GPT-4 Turbo com Visão** - Imagens de alta qualidade
    - **GPT-4o-mini** - Versão econômica com visão
    
    Veja mais em: `docs/GUIA_VISAO_AVANCADA.md`
    """)

# Uploads de múltiplos tipos de mídia
col1, col2, col3 = st.columns(3)

with col1:
    uploaded_pdf = st.file_uploader('📄 PDF', type=['pdf'], key='pdf_upload')

with col2:
    uploaded_image = st.file_uploader('📷 Imagem', type=['png', 'jpg', 'jpeg', 'gif', 'webp'], key='image_upload')

with col3:
    st.write('')  # Espaço
    st.write('')
    col_audio, col_video = st.columns(2)
    with col_audio:
        uploaded_audio = st.file_uploader('🎤 Áudio', type=['mp3', 'wav', 'm4a', 'ogg'], key='audio_upload')
    with col_video:
        uploaded_video = st.file_uploader('🎬 Vídeo', type=['mp4', 'webm', 'mov'], key='video_upload')

def call_model(prompt, img_data=None):
    # Buscar notas relevantes ANTES de fazer a pergunta (apenas se não tiver imagem/vídeo/áudio)
    if not img_data:
        notas_relevantes = memory_store.search_notes(prompt, limit=3)
    else:
        notas_relevantes = []
    
    # Construir contexto com as notas
    contexto = ''
    if notas_relevantes:
        contexto = '\n\n[CONTEXTO DE NOTAS ANTERIORES]\n'
        for nota in notas_relevantes:
            if nota.get('question') and nota.get('answer'):
                contexto += f"\nPergunta: {nota.get('question')}\nResposta: {nota.get('answer')}\n"
            else:
                contexto += f"\nNota: {nota.get('text')}\n"
        contexto += '\n[FIM DO CONTEXTO]\n\n'
    
    # Montar prompt com contexto (simples, sem adicionar "Pergunta do usuario")
    prompt_final = contexto + prompt if contexto else prompt
    
    # Chamar modelo selecionado
    provider = st.session_state.get('current_provider', 'Local')
    model = st.session_state.get('current_model', 'Ollama')
    resultado = model_manager.generate(provider, model, prompt_final, img_data)
    
    # Se for streaming (local), processar linha por linha
    if hasattr(resultado, '__iter__') and not isinstance(resultado, str):
        full_response = ''
        response_placeholder = st.empty()
        for chunk in resultado:
            full_response += chunk
            response_placeholder.markdown(full_response)
    else:
        # Se for GPT/Gemini/Claude (não-streaming), exibir resposta completa
        full_response = resultado
        st.markdown(full_response)
    
    st.session_state.last_question = prompt
    st.session_state.last_answer = full_response

def extract_pdf_text(pdf_file):
    text = ''
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

if st.button('Enviar'):
    if user_input.strip():
        # Processar com mídia se houver upload
        if uploaded_image:
            st.info('📷 Processando imagem...')
            img_data = uploaded_image.read()
            call_model(f'Imagem: {user_input}', img_data=img_data)
            
        elif uploaded_video:
            st.info('🎬 Processando vídeo...')
            st.warning('⚠️ Processamento de vídeo pode levar mais tempo. Use GPT-4o para melhores resultados.')
            video_data = uploaded_video.read()
            call_model(f'Vídeo: {user_input}', img_data=video_data)
            
        elif uploaded_audio:
            st.info('🎤 Processando áudio...')
            audio_data = uploaded_audio.read()
            call_model(f'Áudio: {user_input}', img_data=audio_data)
            
        elif uploaded_pdf:
            st.info('📄 Extraindo PDF...')
            pdf_text = extract_pdf_text(uploaded_pdf)
            call_model(f'PDF:\n{pdf_text}\n\nPergunta:\n{user_input}')
        
        else:
            # Sem mídia, apenas texto
            call_model(user_input)


