FROM lambci/lambda:build-python3.8

# Make this the default working directory
WORKDIR /var/task
# RUN mkdir static

# Expose tcp network port 8000 for debugging
EXPOSE 5000

# Fancy prompt to remind you are in zappashell
RUN echo 'export PS1="\[\e[36m\]zappashell>\[\e[m\]"' >> /root/.bashrc

CMD ["bash"]
