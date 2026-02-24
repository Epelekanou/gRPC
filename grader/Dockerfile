FROM python:3.13-slim

WORKDIR /grader

COPY grader/requirements.txt /grader/requirements.txt
RUN pip install --no-cache-dir -r /grader/requirements.txt

# We need access to the student's generated stubs and proto package
# and (optionally) any shared code layout.
COPY proto /grader/proto
COPY grader /grader/grader
COPY sensor /grader/sensor

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/grader
CMD ["bash", "/grader/grader/run_grader.sh"]
